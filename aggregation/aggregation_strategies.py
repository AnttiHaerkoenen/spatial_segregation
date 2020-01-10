import os
from pathlib import Path

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

from spatial_segregation.analysis import plot_density, kernel_density_surface
from spatial_segregation.data import merge_dataframes, split_plots, aggregate_sum, prepare_pop_data


def get_aggregate_locations(
        *,
        population_data: pd.DataFrame,
        location_data: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    geodata_by_district = []

    for district in set(population_data['district']):
        pop = population_data[population_data.district == district]
        loc = location_data.geometry[location_data.district == district]

        geodata_by_district.append(_get_aggregate_locations_by_district(pop, loc))

    geodata = pd.concat(geodata_by_district, ignore_index=True)
    geodata.crs = location_data.crs

    return geodata


def interval_sample(iterable, length) -> list:
    ratio = len(iterable) / length
    sample = []

    last_int = None
    for i, n in enumerate(iterable):
        integer = i // ratio

        if integer != last_int:
            last_int = integer
            sample.append(n)

    return sample


def _get_aggregate_locations_by_district(
        population_data: pd.DataFrame,
        locations: gpd.GeoSeries,
) -> gpd.GeoDataFrame:

    len_pop = len(population_data.index)
    len_loc = len(locations)

    if len_loc == 0 or len_pop == 0:
        return gpd.GeoDataFrame()

    elif len_loc == len_pop:
        geodata = gpd.GeoDataFrame(population_data)
        geodata = geodata.set_geometry(locations)
        return geodata

    elif len_loc < len_pop:
        # todo
        pass

    elif len_pop < len_loc:
        sample_locations = gpd.GeoSeries(interval_sample(locations, len_pop))
        geodata = gpd.GeoDataFrame(population_data)
        geodata = geodata.set_geometry(sample_locations)

        return geodata


if __name__ == '__main__':
    data_dir = Path('../data')

    district_codes = pd.read_csv(data_dir / 'district_codes.csv')
    district_codes = {k: v for k, v in district_codes.itertuples(index=False)}

    points = gpd.read_file(data_dir / 'intermediary' / 'plots_points_1878.shp')
    points = split_plots(points, target_col='NUMBER')
    points['district'] = [district_codes[int(d)] for d in points['DISTRICT']]
    points['plot_number'] = [str(i) for i in points['NUMBER']]

    pop_by_plot = pd.read_excel(data_dir / 'raw' / 'pop_by_plot_1880.xlsx').pipe(prepare_pop_data)
    pop_by_plot['plot_number'] = [str(n).split(',')[0] for n in pop_by_plot['plot_number']]

    pop_by_page = pd.read_excel(data_dir / 'raw' / 'pop_by_page_1880.xlsx').pipe(prepare_pop_data)

    pop_by_district = pd.read_excel(data_dir / 'raw' / 'pop_by_district_1880.xlsx').pipe(prepare_pop_data)

    plot_data = merge_dataframes(
        location_data=points,
        other_data=pop_by_plot,
        on_location='district plot_number'.split(),
        on_other='district plot_number'.split(),
    )
    plot_data.to_csv(data_dir / 'processed' / 'plot_data_1880.csv')

    page_data = get_aggregate_locations(
        population_data=pop_by_page,
        location_data=points,
    )

    # plots_surface = kernel_density_surface(
    #     ,
    #     group=,
    #     bandwidth=,
    #     cell_size=,
    #     kernel_function=,
    # )
    # todo kde + visualisation
