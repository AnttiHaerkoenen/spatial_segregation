import os

import pandas as pd
import geopandas as gpd
from segregation.spatial import SpatialMinMax
from bokeh.plotting import figure, show, save
from bokeh.models import GeoJSONDataSource

from spatial_segregation.data import merge_dataframes, prepare_pop_data, prepare_point_data, aggregate_sum


def get_xy(
        geodf: gpd.GeoDataFrame,
        geometry_col: str = 'geometry',
) -> gpd.GeoDataFrame:
    geodf['x'] = geodf[geometry_col].apply(lambda geom: tuple(geom.exterior.coords.xy[0]))
    geodf['y'] = geodf[geometry_col].apply(lambda geom: tuple(geom.exterior.coords.xy[1]))
    return geodf


def plot_density(
        data,
        *,
        year,
        group,
        crs=None,
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
    pop_src = GeoJSONDataSource(geojson=pop.to_json())

    fig.patches(
        xs='x',
        ys='y',
        source=water_src,
        fill_color='#59d0ff',
        fill_alpha=0.8,
        line_color=None,
        line_width=0,
    )

    show(fig)


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
    plot_density(data, group='orthodox', year=1880)
