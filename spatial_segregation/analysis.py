import os

import numpy as np
import pandas as pd
import geopandas as gpd
from segregation.aspatial import MinMax
from bokeh.plotting import figure, show, save
from bokeh.models import GeoJSONDataSource
from bokeh.palettes import grey
from scipy.spatial.distance import cdist

from spatial_segregation.data import merge_dataframes, prepare_pop_data, prepare_point_data, aggregate_sum


def get_xy(
        geodf: gpd.GeoDataFrame,
        geometry_col: str = 'geometry',
) -> gpd.GeoDataFrame:
    if geodf[geometry_col].geom_type[0] == 'Point':
        geodf['x'] = geodf[geometry_col].apply(lambda geom: geom.x)
        geodf['y'] = geodf[geometry_col].apply(lambda geom: geom.y)
    else:
        geodf['x'] = geodf[geometry_col].apply(lambda geom: tuple(geom.exterior.coords.xy[0]))
        geodf['y'] = geodf[geometry_col].apply(lambda geom: tuple(geom.exterior.coords.xy[1]))
    return geodf


def gaussian(u, bw):
    return 1 / (np.sqrt(2 * np.pi) * bw ** 2) * np.exp(- u ** 2 / (2 * bw ** 2))


def box(u, bw):
    return np.where(np.abs(u) <= bw, 1, 0)


def triangle(u, bw):
    return np.where(np.abs(u) <= bw, 1 - u/bw, 0)


def biweight(u, bw, alpha=1):
    return np.where(np.abs(u) <= bw, ((bw ** 2 - u ** 2) / (bw ** 2 + u ** 2)) ** alpha, 0)


def kernel_density_surface(
        data,
        group,
        bandwidth,
        cell_size,
        kernel_function,
):
    pop = get_xy(data)
    pad = bandwidth * 2
    minx, miny, maxx, maxy = pop['geometry'].total_bounds
    minx -= pad
    miny -= pad
    maxx += pad
    maxy += pad

    x = np.arange(minx, maxx, cell_size)
    y = np.arange(miny, maxy, cell_size)
    X, Y = np.meshgrid(x, y)
    xy = np.vstack([Y.ravel(), X.ravel()]).T
    U = cdist(xy, pop[['y', 'x']].values, metric='euclidean')
    W = kernel_function(U, bandwidth)
    density = (W * pop[group].values).sum(axis=1).reshape(X.shape)
    return density


def plot_density(
        data,
        *,
        year,
        group,
        kernel_function,
        cell_size,
        crs=None,
        bandwidth,
):
    if crs is None:
        crs = {'init': 'epsg:3067'}

    pop = get_xy(data)
    pad = bandwidth * 2
    minx, miny, maxx, maxy = pop['geometry'].total_bounds
    minx -= pad
    miny -= pad
    maxx += pad
    maxy += pad
    w, h = maxx - minx, maxy - miny

    fig = figure(
        title=f"Density of {group.capitalize()} population in Vyborg in {year}",
        x_range=(minx, maxx),
        y_range=(miny, maxy),
    )
    fig.xaxis.major_tick_line_color = None
    fig.xaxis.minor_tick_line_color = None
    fig.yaxis.major_tick_line_color = None
    fig.yaxis.minor_tick_line_color = None

    fig.xaxis.major_label_text_font_size = '0pt'
    fig.yaxis.major_label_text_font_size = '0pt'

    fig.xgrid.visible = False
    fig.ygrid.visible = False

    water = gpd.read_file('water_clip.shp')
    water.crs = {'init': 'epsg:4326'}
    water.geometry = water.geometry.to_crs(crs)
    water = get_xy(water)
    water_src = GeoJSONDataSource(geojson=water.to_json())

    density = kernel_density_surface(
        data,
        group=group,
        bandwidth=bandwidth,
        cell_size=cell_size,
        kernel_function=kernel_function,
    )

    fig.image(
        [density],
        minx,
        miny,
        w,
        h,
        palette=grey(10)[::-1],
    )
    fig.patches(
        xs='x',
        ys='y',
        source=water_src,
        fill_color='#59d0ff',
        fill_alpha=0.8,
        line_color=None,
        line_width=0,
    )

    return fig


def get_s(
        data,
):
    density_total = kernel_density_surface(
        data,
        group='total',
        bandwidth=100,
        cell_size=10,
        kernel_function=biweight,
    )
    density_orthodox = kernel_density_surface(
        data,
        group='orthodox',
        bandwidth=100,
        cell_size=10,
        kernel_function=biweight,
    )
    density = pd.DataFrame({'orthodox': density_orthodox.flatten(), 'total': density_total.flatten()})
    s = MinMax(density, 'orthodox', 'total')
    return s


if __name__ == '__main__':
    os.chdir('../data')
    points = gpd.read_file('points1878.geojson')
    year = 1920
    points['geometry'].crs = {'init': 'epsg:3067'}
    points = prepare_point_data(points, 'NUMBER', 'NUMBER2')
    pop_data = prepare_pop_data(pd.read_csv(f'{year}.csv'))
    pop_data = aggregate_sum(pop_data, ['plot_number'], [
        'other_christian', 'orthodox', 'other_religion', 'lutheran',
    ])
    data = merge_dataframes(
        location_data=points,
        other_data=pop_data,
        on_location='NUMBER',
        on_other='plot_number',
    )
    data = data[[
        'OBJECTID', 'NUMBER', 'geometry',
        'other_christian', 'orthodox', 'other_religion', 'lutheran',
    ]]
    data['total'] = data[['other_christian', 'orthodox', 'other_religion', 'lutheran']].sum(axis=1)
    s = get_s(data)
    print(s.statistic)
    fig = plot_density(
        data,
        group='orthodox',
        year=year,
        kernel_function=biweight,
        bandwidth=100,
        cell_size=10,
    )
    save(fig, f'../slideshow/orthodox_{year}.html')
    fig = plot_density(
        data,
        group='total',
        year=year,
        kernel_function=biweight,
        bandwidth=100,
        cell_size=10,
    )
    save(fig, f'../slideshow/total_{year}.html')
