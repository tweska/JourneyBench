#!/usr/bin/env python3
import pathlib

import osmium
import networkx as nx
from scipy.spatial import KDTree
from shapely.geometry import Polygon, Point

from .util import haversine, latlon2xyz


class OSMHandler(osmium.SimpleHandler):
    def __init__(self, graph, poly):
        super(OSMHandler, self).__init__()
        self.graph = graph
        self.poly = poly

    def way(self, w):
        if 'highway' not in w.tags:
            return

        for i in range(len(w.nodes) - 1):
            a = w.nodes[i]
            b = w.nodes[i + 1]

            # Skip if edge is (partly) outside the target polygon.
            if self.poly is not None and (
                not self.poly.contains(Point(a.location.lon, a.location.lat)) or
                not self.poly.contains(Point(b.location.lon, b.location.lat))
            ):
                continue

            self.graph.add_node(f'__OSM_{a.ref}', lat=a.location.lat, lon=a.location.lon)
            self.graph.add_node(f'__OSM_{b.ref}', lat=b.location.lat, lon=b.location.lon)
            self.graph.add_edge(f'__OSM_{a.ref}', f'__OSM_{b.ref}')


def osm2nx(osm_file_path: pathlib.Path, poly: Polygon = None) -> nx.Graph:
    """
    Read a `.osm.pbf` file and convert it into a NetworkX Graph.
    :param osm_file_path: path to `.osm.pbf` file
    :param poly: polygon to use during parsing, nodes outside polygon are ignored
    :return: the resulting NetworkX Graph
    """
    graph = nx.Graph()
    handler = OSMHandler(graph, poly)
    handler.apply_file(osm_file_path, locations=True)
    return graph


def combine(G: nx.Graph, G_other: nx.Graph) -> None:
    """
    Combine two NetworkX graphs and connect all nodes from the second graph to
    the nearest node in the first graph, result are stored in the first graph.
    :param G: first NetworkX Graph, result is stored here
    :param G_other: second NetworkX Graph
    """
    nodes = [(v, latlon2xyz(data['lat'], data['lon'])) for v, data in G.nodes(data=True)]
    tree = KDTree(list(zip(*nodes))[1])

    for u, data in G_other.nodes(data=True):
        v = nodes[tree.query(latlon2xyz(data['lat'], data['lon']))[1]][0]
        G.add_node(u, lat=data['lat'], lon=data['lon'], keep=True)
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
