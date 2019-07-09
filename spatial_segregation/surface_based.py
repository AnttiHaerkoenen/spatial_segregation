import os

import numpy as np
import pandas as pd
import geopandas as gpd
from matplotlib import pyplot as plt
import segregation
from shapely.geometry import MultiPoint, Point

from kernels import Kernel, QuarticKernel
from kde import KDESurface


def surface_dissim(
        data: gpd.GeoDataFrame,
        group_1_pop_var: str,
        group_2_pop_var: str,
        kernel: Kernel,
        cell_size,
        polygon=None,
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
    data['group_1_pop_var'] = data['group_1_pop_var'] / sum_1
    sum_2 = data['group_2_pop_var'].sum()
    data['group_2_pop_var'] = data['group_2_pop_var'] / sum_2
    group_surface = KDESurface(data, 'group_1_pop_var', kernel, cell_size, polygon=polygon)
    total_surface = KDESurface(data, 'group_2_pop_var', kernel, cell_size, polygon=polygon)
    surfaces = np.dstack([group_surface.grid, total_surface.grid])

    core_data = data[['group_1_pop_var', 'group_2_pop_var', 'geometry']]

    v_union = np.max(surfaces, axis=2).sum()
    v_intersection = np.min(surfaces, axis=2).sum()
    s = 1 - v_intersection / v_union

    return s, core_data


if __name__ == '__main__':
    os.chdir('../data')
    data_dict = {
        'geometry': [Point(1, 2), Point(2, 3), Point(3, 3)],
        'pop1': [1, 2, 3],
        'pop2': [0, 1, 1],
    }
    data = gpd.GeoDataFrame.from_dict(data_dict)
    kern = QuarticKernel(bandwidth=1.2)
    s, _ = surface_dissim(data, kernel=kern, cell_size=1.2, group_1_pop_var='pop1', group_2_pop_var='pop2')
    print(s)
