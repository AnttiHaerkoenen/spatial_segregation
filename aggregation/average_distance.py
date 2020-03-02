from pathlib import Path
from itertools import chain

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

from spatial_segregation.data import split_plots

if __name__ == '__main__':
    data_dir = Path('../data/')
    point_data = gpd.read_file(data_dir / 'intermediary' / 'plots_points_1878.shp')

    districts = set(point_data.DISTRICT)
    distances = []

    for dist in districts:
        dist_distances = []
        points = point_data.geometry[point_data.DISTRICT == dist]

        for first, second in zip(points, points[1:]):
            dist_distances.append(first.distance(second))

        distances.append(dist_distances)

    dist_data = pd.Series(chain.from_iterable(distances))

    dist_data.plot.kde(xlim=(0, 500))
    plt.show()
