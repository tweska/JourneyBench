import math
from typing import Any, List, Tuple

import networkx as nx
import osmnx as ox
from scipy.spatial import KDTree


def haversine(lat_a: float, lon_a: float, lat_b: float, lon_b: float, r: float = 6371008.7714) -> float:
    """
    Calculate the great-circle distance between two points on a sphere.
    :param lat_a: latitude of first point
    :param lon_a: longitude of first point
    :param lat_b: latitude of second point
    :param lon_b: longitude of second point
    :param r: radius of the sphere, default is the mean radius of Earth in meters as defined by the IUGG (Geodetic Reference System 1980)
    :return: distance between first and second points (in meters)
    """
    p = math.pi / 180
    return 2 * r * math.asin(min(1, math.sqrt(
        math.sin((lat_b-lat_a)/2*p)**2 + math.cos(lat_a*p) * math.cos(lat_b*p) * math.sin((lon_b-lon_a)/2*p)**2
    )))


def osm_graph_from_bbox(north: float, east: float, south: float, west: float) -> nx.Graph:
    """
    Obtain a NetworkX Graph from OpenStreetMaps footpath data.
    :param north: maximum latitude
    :param east: maximum longitude
    :param south: minimum latitude
    :param west: minimum longitude
    :return: an undirected NetworkX Graph
    """
    M = ox.graph_from_bbox(
        north, south, east, west,
        network_type='walk',
        simplify=False,
        retain_all=True,
        truncate_by_edge=False,
    )

    G = nx.Graph()
    G.add_nodes_from([(f'__OSM_{v}', {'lat': d['y'], 'lon': d['x']}) for v, d in M.nodes(data=True)])
    G.add_edges_from([(f'__OSM_{u}', f'__OSM_{v}') for u, v in M.edges(data=False) if u is not v])
    return G


def set_distance(G: nx.Graph) -> None:
    """
    Set the distance in meters for each edge.
    :param G: a NetworkX Graph with attributes 'lat' and 'lon' on nodes
    :return:
    """
    for u, v in G.edges(data=False):
        G.edges[u, v]['distance'] = haversine(G.nodes[u]['lat'], G.nodes[u]['lon'],
                                              G.nodes[v]['lat'], G.nodes[v]['lon'])


def contract(G: nx.Graph, rounds=100, verbose=False) -> nx.Graph:
    """
    Create a simplified version of the graph with no edges with a degree less
    than 3 and all connected components containing at least one transit stops.
    :param G: NetworkX Graph with attribute 'distance' on edges
    :param rounds: maximum number of iterations to run the contraction
    :param verbose: print helpful messages
    :return: a contracted copy of the original graph
    """
    # Remove all connected components without a transit stop.
    if verbose:
        print("Remove connected components without a transit stop...")
    cc = list(nx.connected_components(G))
    fc = [c for c in cc if any([G.nodes[v].get('keep') is True for v in c])]
    G = G.subgraph(v for c in fc for v in c).copy()

    # Remove all nodes with a degree less than 3.
    for i in range(rounds):
        count = 0
        for v, keep in list(G.nodes(data='keep', default=False)):
            d = G.degree[v]
            if keep or d >= 3:
                continue
            if d == 2:  # not a dead-end, must replace edges
                (_, u), (_, w) = G.edges(v)
                if G.has_edge(u, w):  # edge already exists, just update distance
                    G.edges[u, w]['distance'] = min(G.edges[u, w]['distance'],
                                                    G.edges[u, v]['distance'] + G.edges[v, w]['distance'])
                else:
                    G.add_edge(u, w, distance=G.edges[u, v]['distance'] + G.edges[v, w]['distance'])
            G.remove_node(v)
            count += 1
        if verbose:
            print(f"Contraction round {i} completed, removed {count} nodes!")
        if count == 0:
            break

    return G


def add_stops(G: nx.Graph, stops: List[Tuple[Any, float, float]]) -> None:
    """
    Add a list of stops to the footpath graph.
    :param G: footpath graph as NetworkX Graph
    :param stops: list of stops, each as a 3-tuple: id, latitude, longitude
    :return:
    """
    nodes = [(v, (data['lat'], data['lon'])) for v, data in G.nodes(data=True)]
    tree = KDTree(list(zip(*nodes))[1])

    for u, lat, lon in stops:
        v = nodes[tree.query((lat, lon))[1]][0]
        G.add_node(u, lat=lat, lon=lon, keep=True)
        G.add_edge(u, v)


def combine(stops: List[Tuple[Any, float, float]], verbose=False) -> nx.Graph:
    """
    Combine a list of transit-stops with OpenStreetMaps footpath data.
    :param stops: list of stops, each as a 3-tuple: id, latitude, longitude
    :param verbose: print helpful messages
    :return: transfer graph as a NetworkX Graph
    """
    # Determine bounding box.
    north = max(list(zip(*stops))[1])
    south = min(list(zip(*stops))[1])
    east = max(list(zip(*stops))[2])
    west = min(list(zip(*stops))[2])

    # Obtain the graph, add stops and simplify.
    if verbose:
        print("Obtaining initial graph...")
    G = osm_graph_from_bbox(north, east, south, west)
    if verbose:
        print("Adding stops...")
    add_stops(G, stops)
    if verbose:
        print("Setting distances...")
    set_distance(G)
    if verbose:
        print("Contracting graph...")
    G = contract(G, verbose=verbose)

    return G
