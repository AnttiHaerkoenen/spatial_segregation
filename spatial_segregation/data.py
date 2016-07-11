import random
import os

import pandas as pd
import pysal

import kde
import segregation_indices

DATA_DIR = 'data'


def add_coordinates(population_data, point_data):
    data_dict = {}

    for row in point_data:
        data_dict[row[0]] = {'x': row[1], 'y': row[2]}

    for r in population_data:
        if r[0] in data_dict.keys():
            data_dict[r[0]]['host'] = r[1]
            data_dict[r[0]]['other'] = r[2]

    bad_keys = [key
                for key in data_dict
                if key not in [r[0] for r in population_data]]

    for key in bad_keys:
        del data_dict[key]

    return pd.DataFrame.from_dict(data_dict, orient='index')


def shuffle_data(data_frame):
    data = data_frame.copy()
    for _ in data.index:
        i1 = random.choice(data.index)
        i2 = random.choice(data.index)
        for c in list('xy'):
            data.loc[i1, c] = data.loc[i2, c]

    return data


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
    Cleans population data for use in segregation analysis.

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
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    os.chdir(os.path.join(os.path.abspath(os.path.pardir), DATA_DIR))

    point_shp = pysal.open("points.shp")
    point_db = pysal.open("points.dbf", 'r')

    pp = [[point_db[i][0][1], point_shp[i][0], point_shp[i][1]]
          for i in range(len(point_shp))]

    v80 = aggregate_sum(reform(pd.read_csv('1880.csv', sep='\t')))
    v00 = aggregate_sum(reform(pd.read_csv('1900.csv', sep='\t')))
    v20 = aggregate_sum(reform(pd.read_csv('1920.csv', sep='\t')))

    d80 = add_coordinates(v80, pp)
    d00 = add_coordinates(v00, pp)
    d20 = add_coordinates(v20, pp)

    data = {
        1880: d80,
        1900: d00,
        1920: d20
    }

    print(data[1880].data)

    kde1 = kde.KDESurface(d80, 100)
    s = shuffle_data(data[1880])
    kde2 = kde.KDESurface(s, 100)


if __name__ == '__main__':
    main()
