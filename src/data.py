import os

import pandas as pd
import numpy as np
import json

from src import utils
from .exceptions import SSKeyError

DATA_DIR = 'data'
X, Y = 0, 1


class SpatialSegregationData:
    def __init__(
            self,
            location_data,
            population_data
    ):
        """
        Data wrapper for spatial segregation analysis
        :param location_data: LocationData instance or similar
        :param population_data: PopulationData instance or similar
        """
        self._data = self._combine_data(location_data, population_data)

    @staticmethod
    def _combine_data(
            population_data,
            point_data,
            pop_index=0,
            host=1,
            other=2,
            point_index='NUMBER',
            coordinates_to_meters=False,
            false_easting=0,
            false_northing=0
    ):
        data_dict = {}

        for feature in point_data['features']:
            index = feature['properties'][point_index]
            x, y = feature['geometry']['coordinates']
            if coordinates_to_meters:
                x, y = utils.degrees_to_meters(x, y, false_easting=false_easting, false_northing=false_northing)
            data_dict[index] = {'x': x, 'y': y}

        for r in population_data:
            if r[pop_index] in data_dict.keys():
                data_dict[r[pop_index]]['host'] = r[host]
                data_dict[r[pop_index]]['other'] = r[other]

        bad_keys = [key for key in data_dict
                    if key not in [r[pop_index]for r in population_data]]

        for key in bad_keys:
            del data_dict[key]

        return pd.DataFrame.from_dict(data_dict, orient='index').reindex_axis("x y host other".split(), axis='columns')

    @staticmethod
    def shuffle_data(data_frame, columns=("host", "other")):
        pop_columns = list(columns)
        cols = data_frame.columns.values.tolist()
        xy = data_frame.loc[:, list('xy')].values
        pop = data_frame.loc[:, pop_columns].values
        np.random.shuffle(xy)
        return pd.DataFrame(np.hstack((xy, pop)), columns=cols)

    @staticmethod
    def _aggregate_sum(data, group_index=0):
        cols = len(data[0])
        data_rows = [i for i in range(cols) if i != group_index]
        aggregated_data = []
        last_id = None

        for row in data:
            if row[group_index] == last_id:
                for k in data_rows:
                    aggregated_data[-1][k] += row[k]
            else:
                aggregated_data.append(row)
            last_id = row[group_index]

        return aggregated_data

    @staticmethod
    def _reform(population_data, districts='all'):
        if districts == 'all':
            districts = list(set(population_data['district']))
        elif isinstance(districts, str):
            districts = districts.split()
        else:
            districts = list(districts)

        try:
            population_data = population_data[population_data['district'].isin(districts)]
        except KeyError:
            raise SSKeyError("District column not found!")

        pop_data = population_data.fillna(value=0)
        pop_data = pop_data.loc[:, ['plot.number', 'total.men', 'total.women', 'orthodox', 'other.christian',
                                    'other.religion']].astype(int)
        pop_data['lutheran'] = (pop_data['total.men'] + pop_data['total.women'] - pop_data['orthodox'] -
                                pop_data['other.christian'] - pop_data['other.religion'])
        pop_data = pop_data.loc[:, ['plot.number', 'lutheran', 'orthodox']]
        return [i for i in map(list, pop_data.values)]


class LocationData:
    def __init(self, data_frame):
        self._data = data_frame


class PopulationData:
    def __init__(self, data_frame):
        self._data = data_frame


########################################################################################################################

def get_limits(data_frame, variable):
    x = data_frame[variable]

    max_ = max(x, default=None)
    min_ = min(x, default=None)

    return max_, min_

########################################################################################################################


if __name__ == '__main__':
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    os.chdir(os.path.join(os.path.abspath(os.path.pardir), DATA_DIR))

    pop_data = SpatialSegregationData._aggregate_sum(SpatialSegregationData._reform(pd.read_csv('1880.csv')))

    with open('points1878.geojson') as f:
        point_data = json.load(f)

    d = SpatialSegregationData._combine_data(pop_data, point_data)
