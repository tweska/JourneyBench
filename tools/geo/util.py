import math
from typing import List, Tuple

import numpy as np

from scipy.spatial import ConvexHull
from shapely.geometry import Polygon, Point


# Mean radius of Earth in meters derived from the World Geodetic System (WGS 84).
WSG84_R = 6371008.77142


def haversine(
        lat_a: float, lon_a: float,
        lat_b: float, lon_b: float,
        r: float = WSG84_R,
) -> float:
    """
    Calculate the great-circle distance between two points on a sphere.

    :param lat_a: latitude of first point (in degrees)
    :param lon_a: longitude of first point (in degrees)
    :param lat_b: latitude of second point (in degrees)
    :param lon_b: longitude of second point (in degrees)
    :param r: radius of the sphere, default is the mean radius of Earth (in meters)

    :return: distance between first and second points (in meters)
    """
    ta = math.radians(lat_a)
    la = math.radians(lon_a)
    tb = math.radians(lat_b)
    lb = math.radians(lon_b)
    return 2 * r * math.asin(min(1, math.sqrt(
        math.sin((tb - ta) / 2) ** 2 + math.cos(ta) * math.cos(tb) * math.sin((lb - la) / 2) ** 2
    )))


def latlon2AEQ(
        lat_0: float, lon_0: float,
        lat_p: float, lon_p: float
) -> Tuple[float, float]:
    """
    Calculate the Azimuthal Equidistant Projection of a point, based on a centerpoint.
    Source: https://www.samuelbosch.com/2014/02/azimuthal-equidistant-projection.html

    :param lat_0: latitude of the centerpoint (in degrees)
    :param lon_0: longitude of the centerpoint (in degrees)
    :param lat_p: latitude of the point (in degrees)
    :param lon_p: longitude of the point (in degrees)

    :return: projected position of the point as (x, y) coordinates
    """
    t0 = math.radians(lat_0)
    l0 = math.radians(lon_0)
    tp = math.radians(lat_p)
    lp = math.radians(lon_p)

    c = math.acos(math.sin(t0) * math.sin(tp) + math.cos(t0) * math.cos(tp) * math.cos(lp - l0))
    k = c / math.sin(c)

    x = k * math.cos(tp) * math.sin(lp - l0)
    y = k * (math.cos(t0) * math.sin(tp) - math.sin(t0) * math.cos(tp) * math.cos(lp - l0))

    return x, y


def trim_network(input, poly: Polygon):
    from benchmark import Network

    centroid = poly.centroid.y, poly.centroid.x
    points = [latlon2AEQ(*centroid, p[1], p[0]) for p in poly.exterior.coords]
    poly = Polygon(points)

    # Find the nodes that are not contained in the polygon.
    remove = set()
    for i, node in enumerate(input.nodes):
        point = Point(latlon2AEQ(*centroid, node.latitude, node.longitude))
        if not poly.contains(point):
            remove.add(i)

    # Reconstruct the network without the removed nodes.
    output = Network(input.end)
    for i, node in enumerate(input.nodes):
        if i not in remove:
            output.add_node(i, node.latitude, node.longitude, node.stop)
    for conn in input.conns:
        if conn.from_node_id not in remove and conn.to_node_id not in remove:
            output.add_conn(conn.trip_id, conn.from_node_id, conn.to_node_id, conn.departure_time, conn.arrival_time)
    for path in input.paths:
        if path.node_a_id not in remove and path.node_b_id not in remove:
            output.add_path(path.node_a_id, path.node_b_id, path.duration)

    return output


def extended_convex_hull(points: List[Tuple[float, float]], dist: float = 100, r: float = WSG84_R) -> Polygon:
    """
    Create a convex hull around a list of points, extend the hull by a given distance.
    :param points: a list of points (lat, lon) to find the convex hull for
    :param dist: how far to extend the convex hull (in meters)
    :param r: radius of the sphere, default is the mean radius of Earth in meters as defined by the IUGG (Geodetic Reference System 1980)
    :return: a polygon describing the (extended) convex hull
    """
    convex_points = np.array([points[i] for i in ConvexHull(points).vertices])
    if dist == 0:
        return Polygon([(p[1], p[0]) for p in convex_points])

    norm_vectors = []
    for i, v in enumerate(convex_points):
        nu = v - convex_points[(i-1) % len(convex_points)]
        nw = v - convex_points[(i+1) % len(convex_points)]
        vector = (nu / np.linalg.norm(nu)) + (nw / np.linalg.norm(nw))
        norm_vectors.append(vector / np.linalg.norm(vector))
    norm_vectors = np.array(norm_vectors)

    diff = [(math.fabs(math.degrees(dist / (r * math.sin(math.radians(p[1]))))),
             math.fabs(math.degrees(dist / (r * math.cos(math.radians(p[0])))))) for p in convex_points]
    return Polygon([(p[1], p[0]) for p in (convex_points + diff * norm_vectors)])
