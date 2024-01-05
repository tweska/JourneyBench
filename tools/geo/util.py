import math
from typing import Tuple


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


def latlon2xyz(
        lat: float, lon: float,
        r: float = WSG84_R,
) -> Tuple[float, float, float]:
    lat = math.radians(lat)
    lon = math.radians(lon)
    x = r * math.cos(lat) * math.cos(lon)
    y = r * math.cos(lat) * math.sin(lon)
    z = r * math.sin(lat)
    return x, y, z


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
