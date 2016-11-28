import math


def degrees_to_meters(lon, lat, false_easting=0, false_northing=0):
    d_lon = great_circle_distance(lat, 0, lat, lon) - false_easting
    d_lat = great_circle_distance(0, lon, lat, lon) - false_northing
    return d_lon, d_lat


def great_circle_distance(lat1, lon1, lat2, lon2):
    """
    Returns long circle distance between two points using Haversine formula
    :param lat1: latitude of point 1
    :param lon1: longitude of point 1
    :param lat2: latitude of point 2
    :param lon2: longitude of point 2
    :return: distance in meters
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    d_lon = lon2 - lon1
    d_lat = lat2 - lat1
    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    c = 2 * math.asin(a ** 0.5)
    return 6335439 * c


def get_stars(p):
    """
    R-style significance symbols.
    :param p: p-value
    :return: '***', '**', '*', '.' or ' '
    """
    if p < 0 or p > 1:
        raise ValueError("Impossible!")
    elif p <= 0.001:
        return "***"
    elif p <= 0.01:
        return "**"
    elif p <= 0.05:
        return "*"
    elif p <= 0.1:
        return "."
    else:
        return " "
