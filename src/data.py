import os
from typing import Sequence

import pandas as pd
import numpy as np
import geopandas as gpd

from src import utils

DATA_DIR = 'data'


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
            new_geodataframe = new_geodataframe.append(new_row)
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


def merge_dataframes(
        *,
        location_data: gpd.GeoDataFrame,
        other_data: pd.DataFrame,
        on_location,
        on_other,
        **kwargs,
) -> gpd.GeoDataFrame:
    """
    Joins spatial and aspatial dataframes
    :param location_data: geodataframe with locations
    :param other_data: other dataframe
    :param on_location: key for joining
    :param on_other: key for joining
    :param kwargs: additional keyword arguments for pd.DataFrame.merge
    :return:
    """
    if not isinstance(location_data, gpd.GeoDataFrame):
        raise ValueError(f"{location_data}: not a geodataframe")
    if not isinstance(other_data, pd.DataFrame):
        raise ValueError(f"{other_data}: not a dataframe")
    location_data = split_plots(location_data, on_location)
    if location_data.empty:
        raise ValueError("Geodataframe is empty")
    if other_data.empty:
        raise ValueError("Dataframe is empty")

    location_data[on_location] = location_data[on_location].astype(str)
    other_data[on_other] = other_data[on_other].astype(str)
    combined_data = location_data.merge(
        other_data,
        left_on=on_location,
        right_on=on_other,
        **kwargs
    )
    return combined_data


def shuffle_data(data):
    data.geometry = np.random.shuffle(data.geometry)
    return data


def prepare_pop_data(
        population_data: pd.DataFrame,
        cols=None,
) -> pd.DataFrame:
    pop_frame = population_data.fillna(value=0)
    if not cols:
        cols = [
            'plot_number',
            'total_men',
            'total_women',
            'orthodox',
            'other_christian',
            'other_religion',
        ]
    pop_frame.loc[:, cols] = pop_frame.loc[:, cols].astype(int)
    pop_frame['lutheran'] = pop_frame['total_men'] \
        + pop_frame['total_women'] \
        - pop_frame['orthodox'] \
        - pop_frame['other_christian'] \
        - pop_frame['other_religion']
    return pop_frame


def prepare_point_data(
        point_data: gpd.GeoDataFrame,
        number_col='NUMBER',
        number_col_2='NUMBER2',
        na=0,
) -> gpd.GeoDataFrame:
    for i in point_data.index:
        # if (num_2 := point_data.loc[i, number_col_2]) != na:
        num_2 = point_data.loc[i, number_col_2]
        if num_2 != na:
            point_data.loc[i, number_col] = f'{point_data.loc[i, number_col]}, {num_2}'
    del point_data[number_col_2]
    return point_data


########################################################################################################################


if __name__ == '__main__':
    os.chdir(r'../data')

    pop_data = aggregate_sum(
        prepare_pop_data(pd.read_csv('1880.csv')),
        group_cols='district, plot_number'.split(', '),
        target_cols='lutheran, orthodox'.split(', '),
    )

    point_data = prepare_point_data(gpd.read_file('points1878.geojson'))

    d = merge_dataframes(
        location_data=point_data.set_index('OBJECTID'),
        other_data=pop_data,
        on_location='NUMBER',
        on_other='plot_number',
        how='inner',
    )
    print(d)
