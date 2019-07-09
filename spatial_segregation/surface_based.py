import os

import numpy as np
import pandas as pd
import geopandas as gpd
from matplotlib import pyplot as plt
import segregation
from shapely.geometry import MultiPoint, Point

from kernels import Kernel
from kde import KDESurface


def surface_dissim(
        data: gpd.GeoDataFrame,
        group_1_pop_var: str,
        group_2_pop_var: str,
        kernel: Kernel,
        cell_size: int,
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
    data[group_1_pop_var] = data[group_1_pop_var] / data[group_1_pop_var].sum()
    data[group_2_pop_var] = data[group_2_pop_var] / data[group_2_pop_var].sum()
    group_surface = KDESurface(data, group_1_pop_var, kernel, cell_size)
    total_surface = KDESurface(data, group_2_pop_var, kernel, cell_size)
    surfaces = np.dstack(group_surface.grid, total_surface.grid)

    core_data = data[['group_1_pop_var', 'group_2_pop_var', 'geometry']]

    s = 1 - np.min(surfaces, axis=2) / np.max(surfaces, axis=2)

    return s, core_data


if __name__ == '__main__':
    os.chdir('../data')
    data = gpd.GeoDataFrame.from_file('points1878.geojson')
    data.crs = {'init': 'epsg:4067'}
