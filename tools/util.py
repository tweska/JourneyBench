from math import asin, cos, pi, sqrt
from typing import Tuple


def haversine_distance(pos_a: Tuple[float, float], pos_b: Tuple[float, float]) -> float:
    lat_a, lon_a = pos_a
    lat_b, lon_b = pos_b
    p = pi / 180
    r = 6371008.8
    return (2*r)*asin(sqrt(.5-cos((lat_a-lat_b)*p)/2+cos(lat_a*p)*cos(lat_b*p)*(1-cos((lon_a-lon_b)*p))/2))
