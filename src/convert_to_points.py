import os
from pathlib import Path

import geopandas as gpd


def convert_to_points(
        data: gpd.GeoDataFrame,
        crs: dict,
) -> gpd.GeoDataFrame:
    data.geometry = data.geometry.centroid
    data = data.to_crs(crs)
    return data


if __name__ == '__main__':
    data_dir = Path('../data')
    geodata = gpd.read_file(data_dir / 'plots_1878.shp')
    geodata = convert_to_points(geodata, {'init': 'epsg:3067'})
    geodata.to_file(data_dir / 'plots_points_1878.shp')
