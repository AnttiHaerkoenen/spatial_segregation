import os

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import MultiPoint, Point
from libpysal.weights import W, Kernel


def _surface_dissim(
        data: gpd.GeoDataFrame,
        group_1_pop_var: str,
        group_2_pop_var: str,
        w: Kernel = None,
):
    if not isinstance(data, gpd.GeoDataFrame):
        raise TypeError('data should be a geopandas GeoDataFrame')

    if 'geometry' not in data.columns:
        data['geometry'] = data[data._geometry_column_name]
        data = data.drop([data._geometry_column_name], axis=1)
        data = data.set_geometry('geometry')

    data = data.rename(columns={
        group_1_pop_var: 'group_1_pop_var',
        group_2_pop_var: 'group_2_pop_var',
    })
    sum_1 = data['group_1_pop_var'].sum()
    data['group_1_pop_var_norm'] = data['group_1_pop_var'] / sum_1
    sum_2 = data['group_2_pop_var'].sum()
    data['group_2_pop_var_norm'] = data['group_2_pop_var'] / sum_2

    if not w:
        points = [(p.x, p.y) for p in data.centroid]
        w = Kernel(points)

    w_, _ = w.full()

    density_1 = w_ * data['group_1_pop_var_norm'].values
    density_2 = w_ * data['group_2_pop_var_norm'].values
    densities = np.vstack([density_1.sum(axis=1), density_2.sum(axis=1)])
    v_union = densities.max(axis=0).sum()
    v_intersect = densities.min(axis=0).sum()

    s = 1 - v_intersect / v_union

    core_data = data[['group_1_pop_var', 'group_2_pop_var', 'geometry']]

    return s, core_data


if __name__ == '__main__':
    os.chdir('../data')
    data_dict = {
        'geometry': [Point(1, 2), Point(2, 3), Point(3, 3)],
        'pop1': [1, 2, 3],
        'pop2': [0, 1, 1],
    }
    data = gpd.GeoDataFrame.from_dict(data_dict)
    s, _ = _surface_dissim(data, group_1_pop_var='pop1', group_2_pop_var='pop2')
    print(s)
