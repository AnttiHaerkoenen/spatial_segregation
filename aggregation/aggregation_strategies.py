import os
from pathlib import Path
from typing import Callable
from itertools import product

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

from scipy.spatial.distance import cdist
from segregation.aspatial import MinMax

from aggregation.kernels import Martin, Quartic, Box, Triangle
from spatial_segregation.analysis import plot_density, get_xy
from spatial_segregation.data import merge_dataframes,\
    split_plots, prepare_pop_data


def kernel_density_surface(
        data: gpd.GeoDataFrame,
        group: str,
        bandwidth,
        cell_size,
        kernel_function: Callable,
):
    import rasterio as rio
    pop = get_xy(data)
    pad = bandwidth * 2

    minx, miny, maxx, maxy = pop.geometry.total_bounds

    minx -= pad
    miny -= pad
    maxx += pad
    maxy += pad

    x = np.arange(minx, maxx, cell_size)
    y = np.arange(miny, maxy, cell_size)

    X, Y = np.meshgrid(x, y)

    xy_A = np.vstack([Y.ravel(), X.ravel()]).T
    xy_B = pop[['y', 'x']].values

    U = cdist(xy_A, xy_B, metric='euclidean')
    W = kernel_function(bandwidth)(U)

    density = (W * pop[group].values).sum(axis=1).reshape(X.shape)

    geotiff_meta = {
        'driver': 'GTiff',
        'count': 1,
        'dtype': 'float64',
        'width': len(x),
        'height': len(y),
        'crs': data.crs,
        'transform': rio.transform.from_bounds(
            west=minx,
            east=maxx,
            north=maxy,
            south=miny,
            width=len(x),
            height=len(y),
        )
    }

    return density[::-1, ], geotiff_meta


def interval_sample(
        iterable,
        length,
) -> list:
    ratio = len(iterable) / length
    sample = []

    last_int = None

    for i, n in enumerate(iterable):
        integer = i // ratio

        if integer != last_int:
            last_int = integer
            sample.append(n)

    assert len(sample) == length

    return sample


def get_aggregate_locations(
        *,
        population_data: pd.DataFrame,
        location_data: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:

    geodata_by_district = []

    for dist in set(population_data['district']):
        pop = population_data[population_data.district == dist]
        loc = location_data[location_data.district == dist]

        pop = pop.reset_index()
        loc = loc.reset_index()

        district = get_aggregate_locations_by_district(pop, loc)

        geodata_by_district.append(district)

    geodata = pd.concat(geodata_by_district, ignore_index=True)
    geodata.crs = location_data.crs

    return geodata


def get_aggregate_locations_by_district(
        population_data: pd.DataFrame,
        location_data: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:

    len_pop = len(population_data.index)
    len_loc = len(location_data.index)

    if len_loc == 0 or len_pop == 0:
        return gpd.GeoDataFrame()

    elif len_loc < len_pop:
        sample_index = interval_sample(
            population_data.index,
            len_loc,
        )
        new_geom = gpd.GeoDataFrame(
            {'geometry': location_data.geometry},
            index=sample_index,
        )

        try:
            new_geom = new_geom.align(
                population_data,
                join='outer',
                method='pad',
            )
        except NotImplementedError:
            return gpd.GeoDataFrame()

        location_data = new_geom

    elif len_pop < len_loc:
        sample_index = interval_sample(
            location_data.index,
            len_pop,
        )
        location_data = location_data.loc[sample_index, ]

    location_data = location_data.reset_index()
    location_data = location_data.drop(
        columns=['level_0',  'index'],
        errors='ignore',
    )
    population_data = population_data.reset_index()
    population_data = population_data.drop(
        columns=['plot_number', 'district'],
        errors='ignore',
    )

    geodata = pd.concat(
        [location_data, population_data],
        axis=1,
    )
    geodata = geodata.drop(
        columns=['index', 'Unnamed: 0'],
        errors='ignore',
    )

    return geodata


def make_kde_surface(
        data,
        group: str,
        file_path: Path,
        **kde_kwargs
) -> None:
    surface, meta = kernel_density_surface(
        data,
        group=group,
        **kde_kwargs
    )

    with rio.open(file_path, 'w', **meta) as fout:
        fout.write(surface, 1)


def get_S(
        data,
        bandwidth,
        cell_size,
        kernel_function,
):
    density_total, _ = kernel_density_surface(
        data,
        group='total',
        bandwidth=bandwidth,
        cell_size=cell_size,
        kernel_function=kernel_function,
    )
    density_orthodox, _ = kernel_density_surface(
        data,
        group='orthodox',
        bandwidth=bandwidth,
        cell_size=cell_size,
        kernel_function=kernel_function,
    )

    density = pd.DataFrame({
            'orthodox': density_orthodox.flatten(),
            'total': density_total.flatten(),
         })
    s = MinMax(density, 'orthodox', 'total')

    return s


def get_multiple_S(
        datasets,
        *,
        bandwidths,
        cell_sizes,
        kernel_functions,
        n: int = 1,
):
    results = []

    for bw, cell, kern in product(bandwidths, cell_sizes, kernel_functions, repeat=n):
        kwargs = dict(
            bandwidth=bw,
            cell_size=cell,
            kernel_function=kern,
        )

        plot_S = get_S(datasets['plot_data'], **kwargs)
        page_S = get_S(datasets['page_data'], **kwargs)

        results.append((
            plot_S.statistic,
            page_S.statistic,
            plot_S.statistic - page_S.statistic,
            bw,
            cell,
            kern.classname,
        ))

    return pd.DataFrame(
        results,
        columns='S_by_plot S_by_page S_difference bandwidth cell function'.split(),
    )


if __name__ == '__main__':
    data_dir = Path('../data')
    fig_dir = Path('../figures')

    district_codes = pd.read_csv(data_dir / 'district_codes.csv')
    district_codes = {k: v for k, v in district_codes.itertuples(index=False)}

    points = gpd.read_file(data_dir / 'intermediary' / 'plots_points_1878.shp')
    points = split_plots(points, target_col='NUMBER')
    points['district'] = [district_codes[int(d)] for d in points['DISTRICT']]
    points['plot_number'] = [str(i) for i in points['NUMBER']]

    # remove plots after 31 from Repola district
    drop_ = points[points.district == 'Repola'].index[31:]
    points = points.drop(drop_)

    pop_by_plot = pd.read_csv(data_dir / 'intermediary' / 'pop_by_plot_1880.csv').pipe(prepare_pop_data)
    pop_by_plot['plot_number'] = [str(n).split(',')[0] for n in pop_by_plot['plot_number']]

    pop_by_page = pd.read_csv(data_dir / 'intermediary' / 'pop_by_page_1880.csv').pipe(prepare_pop_data)

    plot_data = merge_dataframes(
        location_data=points,
        other_data=pop_by_plot,
        on_location='district plot_number'.split(),
        on_other='district plot_number'.split(),
    )

    plot_data['total'] = plot_data[
        ['other_christian', 'orthodox', 'other_religion', 'lutheran']
    ].sum(axis=1)
    plot_data = plot_data.drop(columns=['Unnamed: 0', 'plot_number'])
    plot_data.to_csv(data_dir / 'processed' / 'plot_data_1880.csv')

    page_data = get_aggregate_locations(
        population_data=pop_by_page,
        location_data=points,
    )

    page_data['total'] = page_data[
        ['other_christian', 'orthodox', 'other_religion', 'lutheran']
    ].sum(axis=1)
    page_data.to_csv(data_dir / 'processed' / 'page_data_1880.csv')

    kwargs = dict(
        bandwidth=250,
        cell_size=25,
        kernel_function=Martin,
    )

    make_kde_surface(
        data=plot_data,
        group='lutheran',
        file_path=data_dir / 'processed' / 'lutheran_by_plot.tif',
        **kwargs
    )

    make_kde_surface(
        data=plot_data,
        group='orthodox',
        file_path=data_dir / 'processed' / 'orthodox_by_plot.tif',
        **kwargs
    )

    make_kde_surface(
        data=page_data,
        group='lutheran',
        file_path=data_dir / 'processed' / 'lutheran_by_page.tif',
        **kwargs
    )

    make_kde_surface(
        data=page_data,
        group='orthodox',
        file_path=data_dir / 'processed' / 'orthodox_by_page.tif',
        **kwargs
    )

    multiple_S = get_multiple_S(
        datasets={
            'page_data': page_data,
            'plot_data': plot_data,
        },
        bandwidths=[100, 150, 200, 250, 300],
        cell_sizes=[25],
        kernel_functions=[Martin],
    )

    multiple_S.to_csv(data_dir / 'processed' / 'aggregation_effects_S.csv')

    print(multiple_S)
    print(multiple_S['S_difference'].abs().mean())
