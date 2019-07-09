import math

import pandas as pd
import numpy as np
import shapely.geometry


def degrees_to_meters(lon, lat, false_easting=0, false_northing=0):
    d_lon = great_circle_distance(lat, 0, lat, lon) - false_easting
    d_lat = great_circle_distance(0, lon, lat, lon) - false_northing
    return d_lon * 6335439, d_lat * 6335439


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
    return c


def get_stars(p):
    """
    R-style significance symbols.
    :param p: p-value
    :return: '***', '**', '*', '.' or ''
    """
    if p < 0 or 1 < p:
        raise ValueError("That cannot be a p-value!")
    elif p <= 0.001:
        return "***"
    elif p <= 0.01:
        return "**"
    elif p <= 0.05:
        return "*"
    elif p <= 0.1:
        return "."
    else:
        return ""


def select_by_location(point_data, polygon):
    """
    Select points inside a polygon. CRS must be the same for all inputs!
    :param point_data: data frame of coordinates
    :param polygon: instance of shapely.geometry.polygon.Polygon
    :return: data frame of coordinates
    """
    #######################################################################
    # MURSUT Python 3.8 varten!
    # if (poly_crs := polygon.crs) != (point_crs := point_data.crs):
    #     print(f"Mismatching CRS! {poly_crs} vs {point_crs}")
    #     return
    #######################################################################
    xy = [(row.x, row.y) for row in point_data.itertuples()]

    points = [p for p in xy
              if polygon.contains(shapely.geometry.point.Point(p[0], p[1]))]

    return pd.DataFrame(np.asarray(points), columns=list('xy'))


def make_mask(kde, polygon, outside=True):
    """
    Returns a mask for kde
    :param kde: kernel density surface
    :type kde: KernelDensitySurface
    :param polygon: a polygon polygon to be analysed
    :type polygon: shapely.geometry.polygon.Polygon
    :param outside: sets cells outside of polygon this value
    :type outside: bool
    :return: 2 dim numpy boolean array
    """
    arr = [0 if polygon.contains(shapely.geometry.Point(p.x, p.y)) else 1 for p in kde.itertuples()]
    arr = np.array(arr)

    if not outside:
        arr = np.abs(arr - 1)

    return arr.reshape(kde.shape)


def get_convex_hull(point_data, convex_hull_buffer=0):
    """
    Create a convex hull based on points
    :param convex_hull_buffer: buffer around convex hull, meters
    :param point_data: data frame of coordinates
    :return: a shapely.geometry.polygon.Polygon
    """
    xy = [(row.x, row.y) for row in point_data.itertuples()]

    convex_hull = shapely.geometry.MultiPoint(xy).convex_hull

    return convex_hull.buffer(convex_hull_buffer)

#
# def pop_to_fraction(data_frame, columns=("host", "other")):
#     pop_columns = list(columns)
#
#     xy = data_frame.loc[:, list("xy")].values
#     pop = data_frame.loc[:, pop_columns].values
#     pop_sum = np.nansum(pop, axis=0, keepdims=True)
#     pop = pop / pop_sum
#
#     return pd.DataFrame(np.hstack((xy, pop)), columns=list("xy") + pop_columns)
