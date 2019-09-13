import os

import numpy as np
import pandas as pd
import geopandas as gpd
from segregation.spatial import SpatialMinMax
from bokeh.plotting import figure, show, save
from bokeh.models import GeoJSONDataSource
import libpysal
from libpysal.weights import Kernel

from spatial_segregation.data import merge_dataframes, prepare_pop_data, prepare_point_data, aggregate_sum


def get_xy(
        geodf: gpd.GeoDataFrame,
        geometry_col: str = 'geometry',
) -> gpd.GeoDataFrame:
    if geodf[geometry_col].geom_type[0] == 'Point':
        geodf['x'] = geodf[geometry_col].apply(lambda geom: tuple(geom.coords.xy[0]))
        geodf['y'] = geodf[geometry_col].apply(lambda geom: tuple(geom.coords.xy[1]))
    else:
        geodf['x'] = geodf[geometry_col].apply(lambda geom: tuple(geom.exterior.coords.xy[0]))
        geodf['y'] = geodf[geometry_col].apply(lambda geom: tuple(geom.exterior.coords.xy[1]))
    return geodf


def quartic(u, bandwidth):
    return np.where(np.abs(u) <= bandwidth, bandwidth * 15/16 * (1 - u**2) ** 2, 0)


def plot_density(
        data,
        *,
        year,
        group,
        kernel_function,
        crs=None,
        **kwargs
):
    if crs is None:
        crs = {'init': 'epsg:3067'}
    fig = figure(title=f"Density of {group.capitalize()} population in Vyborg in {year}")

    water = gpd.read_file('water_clip.shp')
    water.crs = {'init': 'epsg:4326'}
    water.geometry = water.geometry.to_crs(crs)
    water = get_xy(water)
    water_src = GeoJSONDataSource(geojson=water.to_json())

    pop = get_xy(data)
    # pop_src = GeoJSONDataSource(geojson=pop.to_json())
    minx, miny, maxx, maxy = pop['geometry'].total_bounds
    x = np.arange(minx, maxx, 50)
    y = np.arange(miny, maxy, 50)
    X, Y = np.meshgrid(x, y)
    xy = np.vstack([Y.ravel(), X.ravel()]).T
    # todo XX YY
    dist = np.sqrt(np.power(X, 2) + np.power(Y, 2))
    density = kernel_function(dist, **kwargs)
    print((XX**2 + YY**2)**0.5)

    fig.patches(
        xs='x',
        ys='y',
        source=water_src,
        fill_color='#59d0ff',
        fill_alpha=0.8,
        line_color=None,
        line_width=0,
    )
    fig.image(density)

    # show(fig)


if __name__ == '__main__':
    os.chdir('../data')
    points = gpd.read_file('points1878.geojson')
    points['geometry'].crs = {'init': 'epsg:3067'}
    points = prepare_point_data(points, 'NUMBER', 'NUMBER2')
    pop_data = prepare_pop_data(pd.read_csv('1920.csv'))
    pop_data = aggregate_sum(pop_data, ['plot_number'], [
        'other_christian', 'orthodox', 'other_religion', 'draft', 'lutheran',
    ])
    data = merge_dataframes(
        location_data=points,
        other_data=pop_data,
        on_location='NUMBER',
        on_other='plot_number',
    )
    data = data[[
        'OBJECTID', 'NUMBER', 'geometry',
        'other_christian', 'orthodox', 'other_religion', 'draft', 'lutheran',
    ]]
    plot_density(data, group='orthodox', year=1880, kernel_function=quartic, bandwidth=100)
