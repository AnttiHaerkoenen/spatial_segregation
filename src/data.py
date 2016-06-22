import random
import os

import pandas as pd
import pysal

import kde
import segregation_indices

DATA_FILE = './spatial_segregation/data'


class Data:
    def __init__(self, population_data, point_data, host_group, other_group, year=None):
        self.population_data = population_data
        self.point_data = point_data
        self.year = year
        self.host = host_group
        self.other = other_group
        self.data = {}

        for row in point_data:
            self.data[row[0]] = {'x': row[1], 'y': row[2]}

        for r in population_data:
            if r[0] in self.data.keys():
                self.data[r[0]]['host'] = r[1]
                self.data[r[0]]['other'] = r[2]

        bad_keys = [key
                    for key in self.data
                    if key not in [r[0] for r in population_data]]

        for key in bad_keys:
            del self.data[key]

    def __str__(self):
        string = ["", "Data set for spatial segregation analysis",
                  "Year: {}\nHost group: {}\nOther group(s): {}"
                      .format(self.year, self.host, self.other)]

        for k, v in self.data.items():
            string.append(
                "Point {0:4d}:\t Coordinates {1:8.2f}, {2:8.2f}\t Host: {3:5d}\t Other: {4:5d}"
                    .format(k, v['x'], v['y'], v['host'], v['other']))

        return '\n'.join(string)

    def __iter__(self):
        return iter(self.data.values())

    def get_data(self, keys='all'):
        """
        Returns data from object
        :param keys: an iterable of keys wanted
        :return: dict of dicts where plot numbers are keys to sub-dicts
        """
        if keys == 'all':
            return self.data
        else:
            return {self.data[k] for k in keys if k in self.data.keys()}

    def get_y_limits(self):
        y_max = y_min = self.data[random.choice(list(self.data.keys()))]['y']

        for v in self.data.values():
            y_max = v['y'] if v['y'] > y_max else y_max
            y_min = v['y'] if v['y'] < y_min else y_min

        return y_max, y_min

    def get_x_limits(self):
        x_max = x_min = self.data[random.choice(list(self.data.keys()))]['x']

        for v in self.data.values():
            x_max = v['x'] if v['x'] > x_max else x_max
            x_min = v['x'] if v['x'] < x_min else x_min

        return x_max, x_min


class SimulatedData(Data):
    def __init__(self, model_data):
        Data.__init__(self, model_data.population_data, model_data.point_data, model_data.host, model_data.other)
        self._shuffle()

    def __str__(self):
        string = ["", "Simulated data for spatial segregation analysis"]

        for k, v in self.data.items():
            string.append(
                "Point {0:4d}:\t Coordinates {1:8.2f}, {2:8.2f}\t Host: {3:5d}\t Other: {4:5d}"
                    .format(k, v['x'], v['y'], v['host'], v['other']))

        return '\n'.join(string)

    def _shuffle(self):
        index = [i for i in self.data.keys()]
        for i in range(len(self.data) * 2):
            i1 = random.choice(index)
            i2 = random.choice(index)
            for co in ('x', 'y'):
                self.data[i1][co], self.data[i2][co] = self.data[i2][co], self.data[i1][co]


########################################################################################################################


def aggregate_sum(data, group=0):
    """
    Calculates aggregate sums so that all the records with from the same address are summed up.
    :param data: list of lists
    :param group: index of group position
    :return: list of lists
    """
    cols = len(data[0])
    data_rows = [i for i in range(cols)]
    data_rows.remove(group)
    aggregated_data = []
    last_id = None

    for row in data:
        if row[group] == last_id:
            for k in data_rows:
                aggregated_data[-1][k] += row[k]
        else:
            aggregated_data.append(row)
        last_id = row[group]

    return aggregated_data


def reform(population_data):
    """
    Cleans population data for use in segregation analysis
    :param population_data:
    :return: Reformed list of lists
    """
    pop_data = population_data.fillna(value=0)
    pop_data = pop_data.loc[:, ['plot.number', 'total.men', 'total.women', 'orthodox', 'other.christian',
                                'other.religion']].astype(int)
    pop_data['lutheran'] = (pop_data['total.men'] + pop_data['total.women'] - pop_data['orthodox'] -
                            pop_data['other.christian'] - pop_data['other.religion'])
    pop_data = pop_data.loc[:, ['plot.number', 'lutheran', 'orthodox']]
    return [i for i in map(list, pop_data.values)]


########################################################################################################################


def main():
    os.chdir(DATA_FILE)

    point_shp = pysal.open("points.shp")
    point_db = pysal.open("points.dbf", 'r')

    pp = [[point_db[i][0][1], point_shp[i][0], point_shp[i][1]]
          for i in range(len(point_shp))]

    v80 = aggregate_sum(reform(pd.read_csv('1880.csv', sep='\t')))
    v00 = aggregate_sum(reform(pd.read_csv('1900.csv', sep='\t')))
    v20 = aggregate_sum(reform(pd.read_csv('1920.csv', sep='\t')))

    d80 = Data(v80, pp, 'lutheran', 'orthodox', 1880)
    d00 = Data(v00, pp, 'lutheran', 'orthodox', 1900)
    d20 = Data(v20, pp, 'lutheran', 'orthodox', 1920)

    data = {
        1880: d80,
        1900: d00,
        1920: d20
    }

    kde1 = kde.KDESurface(d80, 100)
    s = SimulatedData(data[1880])
    kde2 = kde.KDESurface(s, 100)
    # print(kde1.host, '\n', kde2.host)

    ind1 = segregation_indices.Indices(kde1)
    ind2 = segregation_indices.Indices(kde2)


if __name__ == '__main__':
    main()
