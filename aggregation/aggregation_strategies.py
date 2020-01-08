import os
from pathlib import Path

import pandas as pd
import geopandas as gpd

from spatial_segregation.analysis import plot_density, kernel_density_surface
from spatial_segregation.data import merge_dataframes, split_plots, aggregate_sum, prepare_pop_data


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

    pop_by_page = pd.read_excel(data_dir / 'raw' / 'pop_by_page_1880.xlsx')

    pop_by_district = pd.read_excel(data_dir / 'raw' / 'pop_by_district_1880.xlsx')


    # todo combinations
    plot_data = merge_dataframes(
        location_data=points,
        other_data=pop_by_plot,
        on_location='district plot_number'.split(),
        on_other='district plot_number'.split(),
    )

    print(plot_data['lutheran'])

    # plots_surface = kernel_density_surface(
    #     ,
    #     group=,
    #     bandwidth=,
    #     cell_size=,
    #     kernel_function=,
    # )
    # todo kde + visualisation
