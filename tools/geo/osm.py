#!/usr/bin/env python3

from typing import Dict, Tuple

import networkx as nx
import osmnx as ox
from scipy.spatial import KDTree
from shapely.geometry import Polygon

from .util import haversine, latlon2AEQ


def osm_graph_from_poly(poly: Polygon):
    M = ox.graph_from_polygon(
        poly,
        network_type='walk',
        simplify=False,
        retain_all=True,
        truncate_by_edge=False,
    )

    G = nx.Graph()
    G.add_nodes_from([(f'__OSM_{v}', {'lat': d['y'], 'lon': d['x']}) for v, d in M.nodes(data=True)])
    G.add_edges_from([(f'__OSM_{u}', f'__OSM_{v}') for u, v in M.edges(data=False) if u is not v])
    return G


def add_stops(G: nx.Graph, stops: Dict[int, Tuple[float, float]], centroid: Tuple[float, float]) -> None:
    nodes = [(v, latlon2AEQ(*centroid, data['lat'], data['lon'])) for v, data in G.nodes(data=True)]
    tree = KDTree(list(zip(*nodes))[1])

    for u, (lat, lon) in stops.items():
        v = nodes[tree.query(latlon2AEQ(*centroid, lat, lon))[1]][0]
        G.add_node(u, lat=lat, lon=lon, keep=True)
        G.add_edge(u, v)


def set_distance(G: nx.Graph) -> None:
    """
    Set the distance in meters for each edge.
    :param G: a NetworkX Graph with attributes 'lat' and 'lon' on nodes
    """
    for u, v in G.edges(data=False):
        G.edges[u, v]['distance'] = haversine(G.nodes[u]['lat'], G.nodes[u]['lon'],
                                              G.nodes[v]['lat'], G.nodes[v]['lon'])


def contract(G: nx.Graph, rounds=100) -> nx.Graph:
    """
    Create a simplified version of the graph with no edges with a degree less
    than 3 and all connected components containing at least one transit stops.
    :param G: NetworkX Graph with attribute 'distance' on edges
    :param rounds: maximum number of iterations to run the contraction
    :param verbose: print helpful messages
    :return: a contracted copy of the original graph
    """
    # Remove all connected components without a transit stop.
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
        if count == 0:
            break

    return G


def combine(stops: Dict[int, Tuple[float, float]], poly: Polygon) -> nx.Graph:
    G = osm_graph_from_poly(poly)
    add_stops(G, stops, (poly.centroid.y, poly.centroid.x))
    set_distance(G)
    G = contract(G)
    return G
