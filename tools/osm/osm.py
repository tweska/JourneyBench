#!/usr/bin/env python3

import math
from typing import Any, List, Tuple

import networkx as nx
import numpy as np
import osmnx as ox
from scipy.spatial import ConvexHull, KDTree
from shapely.geometry import Polygon


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


def extended_convex_hull(points: List[Tuple[float, float]], dist: float = 1000, r: float = 6371008.7714) -> List[Tuple[float, float]]:
    """
    Create a convex hull around a list of points, extend the hull by a given distance.
    :param points: a list of points (lat, lon) to find the convex hull for
    :param dist: how far to extend the convex hull (in meters)
    :param r: radius of the sphere, default is the mean radius of Earth in meters as defined by the IUGG (Geodetic Reference System 1980)
    :return: a list of points describing the (extended) convex hull
    """
    convex_points = np.array([points[i] for i in ConvexHull(points).vertices])
    if dist == 0:
        return convex_points

    norm_vectors = []
    for i, v in enumerate(convex_points):
        nu = v - convex_points[(i-1) % len(convex_points)]
        nw = v - convex_points[(i+1) % len(convex_points)]
        vector = (nu / np.linalg.norm(nu)) + (nw / np.linalg.norm(nw))
        norm_vectors.append(vector / np.linalg.norm(vector))
    norm_vectors = np.array(norm_vectors)

    diff = [(math.fabs(math.degrees(dist / (r * math.sin(math.radians(p[1]))))),
             math.fabs(math.degrees(dist / (r * math.cos(math.radians(p[0])))))) for p in convex_points]
    return convex_points + diff * norm_vectors


def osm_graph_from_points(points: List[Tuple[float, float]], periphery: float = 1000) -> nx.Graph:
    convex = extended_convex_hull(points, periphery)
    polygon = Polygon([(y, x) for x, y in convex])
    F = ox.graph_from_polygon(
        polygon,
        network_type='walk',
        simplify=False,
        retain_all=True,
        truncate_by_edge=False,
    )

    G = nx.Graph()
    G.add_nodes_from([(f'__OSM_{v}', {'lat': d['y'], 'lon': d['x']}) for v, d in F.nodes(data=True)])
    G.add_edges_from([(f'__OSM_{u}', f'__OSM_{v}') for u, v in F.edges(data=False) if u is not v])
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
    # Obtain the graph, add stops and simplify.
    if verbose:
        print("Obtaining initial graph...")
    G = osm_graph_from_points([(lat, lon) for _, lat, lon in stops])
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


if __name__ == '__main__':
    import argparse
    import pickle

    argparser = argparse.ArgumentParser()
    argparser.add_argument('stops')
    argparser.add_argument('graph')
    args = argparser.parse_args()

    with open(args.stops, 'r') as file:
        stops = [(i, float(a), float(b)) for i, a, b in [line for line in [line.split(' ') for line in file]]]
    if len(stops) < 3:
        exit(-1)

    G = combine(stops, True)
    nodes = {v: data for v, data in G.nodes(data=True)}
    edges = {(u, v): data for u, v, data in G.edges(data=True)}

    print(f"Dumping {len(nodes)} nodes and {len(edges)} edges to '{args.graph}'!")
    with open(args.graph, 'wb') as file:
        pickle.dump((nodes, edges), file)
