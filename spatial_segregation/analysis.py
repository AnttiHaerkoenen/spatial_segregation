import os

import pandas as pd
import geopandas as gpd
from segregation.spatial import SpatialMinMax

from spatial_segregation.data import merge_dataframes, prepare_pop_data, prepare_point_data, aggregate_sum


if __name__ == '__main__':
    os.chdir('../data')
    points = gpd.read_file('points1878.geojson')
    points = prepare_point_data(points, 'NUMBER', 'NUMBER2')
    pop_data = prepare_pop_data(pd.read_csv('1920.csv'))
    pop_data = aggregate_sum(pop_data, ['plot_number'], ['lutheran', 'orthodox'])
    data = merge_dataframes(
        location_data=points,
        other_data=pop_data,
        on_location='NUMBER',
        on_other='plot_number',
    )
    data = data[[
        'OBJECTID', 'NUMBER', 'geometry',
        'upper', 'lower', 'worker_industrial', 'worker_other', 'servants', 'other',
        'other_christian', 'orthodox', 'other_religion', 'draft', 'lutheran',
    ]]
    print(data)
