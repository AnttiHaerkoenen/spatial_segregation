import os

import numpy as np
import pandas as pd
import geopandas as gpd
import segregation
from libpysal.weights import Kernel


def _surface_dissim(
        data: gpd.GeoDataFrame,
        group_pop_var: str,
        total_pop_var: str,
        cell_size: int,
):
    """
    Calculation of Surface Based Dissimilarity index

    Parameters
    ----------

    data          : a geopandas DataFrame with a geometry column.

    group_pop_var : string
                    The name of variable in data that contains the population size of the group of interest

    total_pop_var : string
                    The name of variable in data that contains the total population of the unit

    Returns
    ----------

    statistic : float
                Spatial Dissimilarity Index

    core_data : a geopandas DataFrame
                A geopandas DataFrame that contains the columns used to perform the estimate.

    Notes
    -----
    Based on O'Sullivan & Wong (2007). A Surface‐Based Approach to Measuring Spatial Segregation.
    Geographical Analysis 39: 2. https://doi.org/10.1111/j.1538-4632.2007.00699.x

    """
    if not isinstance(data, gpd.GeoDataFrame):
        raise TypeError('data should be a geopandas GeoDataFrame')

    if 'geometry' not in data.columns:
        data['geometry'] = data[data._geometry_column_name]
        data = data.drop([data._geometry_column_name], axis=1)
        data = data.set_geometry('geometry')

    points = [shape.centroid for shape in data.geometry]
    convex = data.geometry.convex_hull
    envelope = data.geometry.envelope

    data = data.rename(columns={
        group_pop_var: 'group_pop_var',
        total_pop_var: 'total_pop_var'
    })

    ymax, ymin = []
    xmax, xmin = []

    x = np.arange(xmin, xmax, cell_size)
    y = np.arange(ymin, ymax, cell_size)
    y = np.flipud(y)
    x, y = np.meshgrid(x, y)

    flat = x.flatten()[:, np.newaxis], y.flatten()[:, np.newaxis]
    df = pd.DataFrame(np.hstack(flat), columns=list('xy'))

    core_data = data[['group_pop_var', 'total_pop_var', 'geometry']]

    return s, core_data


if __name__ == '__main__':
    os.chdir('../data')
    data = gpd.GeoDataFrame.from_file('points1878.geojson')
    data.crs = {'init': 'epsg:4067'}
    print(data['geometry'].envelope)
