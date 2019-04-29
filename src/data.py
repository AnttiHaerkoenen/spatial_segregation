import os

import pandas as pd
import numpy as np
import geopandas as gpd

from src import utils

DATA_DIR = 'data'
X, Y = 0, 1


def combine_data(
        *,
        location_data: gpd.GeoDataFrame,
        other_data: pd.DataFrame,
        location_index,
        **join_args,
) -> gpd.GeoDataFrame:
    """
    Joins spatial and aspatial dataframes
    :param location_data: geodataframe with locations
    :param other_data: other dataframe
    :param location_index: index for pd.DataFrame.set_index
    :param join_args: kwargs for pd.DataFrame.join
    :return:
    """
    location_data = utils.split_plots(location_data, location_index)
    if isinstance(other_data, pd.DataFrame):
        location_data = location_data.set_index(location_index)
        combined_data = location_data.join(other_data, **join_args)
        return combined_data


def shuffle_data(data):
    data.geometry = np.random.shuffle(data.geometry)
    return data


def prepare_pop_data(
        population_data: pd.DataFrame,
        cols=None,
) -> pd.DataFrame:
    pop_data = population_data.fillna(value=0)
    if not cols:
        cols = [
            'plot_number',
            'total_men',
            'total_women',
            'orthodox',
            'other_christian',
            'other_religion',
        ]
    pop_data.loc[:, cols] = pop_data.loc[:, cols].astype(int)
    pop_data['lutheran'] = pop_data['total_men'] \
                           + pop_data['total_women'] \
                           - pop_data['orthodox'] \
                           - pop_data['other_christian'] \
                           - pop_data['other_religion']
    return pop_data


def get_limits(data_frame, variable):
    x = data_frame[variable]

    max_ = max(x, default=None)
    min_ = min(x, default=None)

    return max_, min_

########################################################################################################################


if __name__ == '__main__':
    os.chdir(r'../data')

    pop_data = utils.aggregate_sum(
        prepare_pop_data(pd.read_csv('1880.csv')),
        group_cols='district, plot_number'.split(', '),
        target_cols='lutheran, orthodox'.split(', '),
    )

    point_data = gpd.read_file('points1878.geojson')

    d = combine_data(
        location_data=point_data,
        other_data=pop_data,
        location_index='NUMBER',
        on='plot_number',
        how='outer',
    )
    print(pop_data)
