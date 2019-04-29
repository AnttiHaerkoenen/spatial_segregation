import math
import logging
from typing import Sequence

import pandas as pd
import geopandas as gpd
import numpy as np
import shapely.geometry


def split_plots(
        geodataframe: gpd.GeoDataFrame,
        target_col: str,
        separator: str = ',',
) -> gpd.GeoDataFrame:
    """
    Splits plot rows in parts by based on separator
    :param geodataframe:
    :param target_col: column name
    :param separator: separator, default ','
    :return: GeoDataFrame with split rows
    """
    new_geodataframe = gpd.GeoDataFrame(columns=geodataframe.columns)
    for _, row in geodataframe.iterrows():
        for c in str(row[target_col]).split(separator):
            new_row = row
            new_row[target_col] = c
            new_geodataframe.append(new_row)
    return new_geodataframe.reindex()


def aggregate_sum(
        data: pd.DataFrame,
        group_cols: Sequence,
        target_cols: Sequence,
) -> pd.DataFrame:
    """
    Calculates aggregate sums of target_cols based grouped by group_cols.
    Preserves crs-attribute if 'data' is GeoDataFrame.
    :param data: target dataframe
    :param group_cols:
    :param target_cols:
    :return:
    """
    agg_data = pd.DataFrame(columns=data.columns)
    if isinstance(data, gpd.GeoDataFrame):
        agg_data.crs = data.crs

    last = pd.Series()
    len_targets = len(target_cols)
    sums = pd.Series(np.zeros(len_targets), index=target_cols)
    for _, row in data.iterrows():
        if row[group_cols].all() != last.all():
            last = row[group_cols]
            new_row = row
            new_row[target_cols] = sums
            sums = pd.Series(np.zeros(len_targets), index=target_cols)
            agg_data = agg_data.append(new_row)
        else:
            sums += row[target_cols]

    return agg_data.reindex()


def combine_data(
        shp_fp: str,
        stats_fp: str,
        shp_on: str = None,
        stats_on: str = None,
        sheet: str or int = None,
        **kwargs
) -> gpd.GeoDataFrame or None:
    """
    Combines spatial and non-spatial data from files using pandas.DataFrame and geopandas.GeoDataFrame.
    :param shp_fp: Filepath to spatial data (shapefile)
    :param stats_fp: Filepath to non-spatial data (csv, xls, xlsx)
    :param shp_on: Which column of spatial data to use in join
    :param stats_on: Which column of non-spatial data to use in join
    :param sheet: which excel sheet to use
    :param kwargs: Additional arguments for pandas.DataFrame.join
    :return: gpd.GeoDataFrame with joined data
    """
    data_ = gpd.read_file(shp_fp)
    with open(shp_fp.replace('.shp', '.prj')) as crs_fin:
        crs_ = crs_fin.readline().strip()
    data_.crs = crs_

    stats_format = stats_fp.split('.', maxsplit=1)[1]
    if stats_format == 'csv':
        data_stats = pd.read_csv(stats_fp)
    elif stats_format in ('xls', 'xlsx'):
        data_stats = pd.read_excel(stats_fp, sheet_name=sheet)
    else:
        print(f'combine_data: {stats_format} is not supported data format')
        return None

    if shp_on:
        try:
            data_ = data_.set_index(shp_on)
        except KeyError:
            print(f"{shp_on} is wrong key. Check spelling")
            return None
    if stats_on:
        try:
            data_stats = data_stats.set_index(stats_on)
        except KeyError:
            print(f"{stats_on} is wrong key. Check spelling")
            return None

    data_ = data_.join(data_stats, **kwargs)
    return data_.reset_index()


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
    :param polygon: a polygon area to be analysed
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
