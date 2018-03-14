import os

import pandas as pd
import numpy as np
import geopandas as gpd
import json

from src import utils
from exceptions import SpatSegKeyError

DATA_DIR = 'data'
X, Y = 0, 1


class SpatialSegregationData:
    def __init__(
            self,
            location_data,
            population_data=None,
    ):
        """
        Data wrapper for spatial segregation analysis
        """
        self._data = self._combine_data(
            location_data=location_data,
            population_data=population_data,
        )

    @staticmethod
    def _combine_data(
            *,
            location_data: gpd.GeoDataFrame,
            population_data: pd.DataFrame=None,
            location_index='NUMBER',
            **kwargs
    ) -> gpd.GeoDataFrame:
        location_data = utils.split_plots(location_data, location_index)
        if population_data:
            location_data = location_data.set_index(location_index)
            location_data = location_data.join(population_data, **kwargs)
        return location_data

        # data_dict = {}
        #
        # for feature in point_data['features']:
        #     index = feature['properties'][point_index]
        #     x, y = feature['geometry']['coordinates']
        #     if coordinates_to_meters:
        #         x, y = utils.degrees_to_meters(x, y, false_easting=false_easting, false_northing=false_northing)
        #     data_dict[index] = {'x': x, 'y': y}
        #
        # for r in population_data:
        #     if r[pop_index] in data_dict.keys():
        #         data_dict[r[pop_index]]['host'] = r[host]
        #         data_dict[r[pop_index]]['other'] = r[other]
        #
        # bad_keys = [key for key in data_dict
        #             if key not in [r[pop_index]for r in population_data]]
        #
        # for key in bad_keys:
        #     del data_dict[key]
        #
        # return pd.DataFrame.from_dict(data_dict, orient='index').reindex_axis("x y host other".split(), axis='columns')

    @staticmethod
    def shuffle_data(data_frame, columns=("host", "other")):
        pop_columns = list(columns)
        cols = data_frame.columns.values.tolist()
        xy = data_frame.loc[:, list('xy')].values
        pop = data_frame.loc[:, pop_columns].values
        np.random.shuffle(xy)
        return pd.DataFrame(np.hstack((xy, pop)), columns=cols)


########################################################################################################################

def get_limits(data_frame, variable):
    x = data_frame[variable]

    max_ = max(x, default=None)
    min_ = min(x, default=None)

    return max_, min_

########################################################################################################################


if __name__ == '__main__':
    os.chdir(r'../data')

    pop_data = utils.aggregate_sum(
        utils.prepare_pop_data(pd.read_csv('1880.csv')),
        group_cols='district, plot.number'.split(', '),
        target_cols='lutheran, orthodox'.split(', '),
    )

    point_data = gpd.read_file('points1878.geojson')

    d = SpatialSegregationData(pop_data, point_data)
    print(d)
