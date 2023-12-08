import math
from typing import Tuple

from shapely import Polygon, Point

from benchmark import Network


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


def trim_network(input: Network, poly: Polygon) -> Network:
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
