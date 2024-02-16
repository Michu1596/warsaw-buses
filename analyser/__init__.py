from math import radians, sin, cos, atan2, sqrt


def distance2(dlon, dlat):
    # The math module contains a function named radians which converts from degrees to radians.
    # The radius of the Earth in Poland is 6363.564 km
    dlon = radians(dlon)
    dlat = radians(dlat)
    R = 6363.564
    # Haversine formula
    a = sin(dlat / 2) ** 2 + cos(dlat) * cos(dlat) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    dist = R * c
    return abs(dist)
