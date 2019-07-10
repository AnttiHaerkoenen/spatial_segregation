import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, MultiPoint
import matplotlib.pyplot as plt

from old.kernels import Kernel, QuarticKernel


class KDESurface:
    def __init__(
            self,
            data: gpd.GeoDataFrame,
            variable: str,
            kernel: Kernel,
            cell_size,
            polygon=None,
    ):
        if not isinstance(data, gpd.GeoDataFrame):
            raise TypeError('data should be a geopandas GeoDataFrame')

        if 'geometry' not in data.columns:
            data['geometry'] = data[data._geometry_column_name]
            data = data.drop([data._geometry_column_name], axis=1)
            data = data.set_geometry('geometry')

        self.polygon = polygon

        data = data.rename(columns={
            variable: 'variable',
        })

        self.cell_size = cell_size
        data.points = data.geometry.centroid
        convex = MultiPoint(data.geometry).convex_hull

        if not self.polygon:
            self.polygon = convex.buffer(kernel.bandwidth)

        xmin, ymin, xmax, ymax = self.bbox = self.polygon.bounds
        x = np.arange(xmin, xmax, self.cell_size)
        y = np.arange(ymin, ymax, self.cell_size)
        y = np.flipud(y)
        x, y = np.meshgrid(x, y)
        self.shape = x.shape
        flat = x.flatten()[:, np.newaxis], y.flatten()[:, np.newaxis]
        df = pd.DataFrame(np.hstack(flat), columns=['x', 'y'])
        outside = [row.Index for row in df.itertuples() if not self.polygon.contains(Point(row.x, row.y))]
        self.df = df.drop(outside)

        self.kernel = kernel
        x1, x2 = np.meshgrid(self.df['x'], data.geometry.x)
        y1, y2 = np.meshgrid(self.df['y'], data.geometry.y)
        self.d = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        self.w = self.kernel(self.d)
        vals = data['variable'].values.reshape(len(data), 1)
        self.df['density'] = np.sum(self.w * vals, axis=0)
        zeros = pd.Series(np.zeros(len(outside)), index=outside)
        grid = self.df['density'].append(zeros, verify_integrity=True).sort_index()
        self.grid = grid.values.reshape(self.shape)

    def __str__(self):
        return f"Kernel density surface," \
            f" kernel: {self.kernel.name}, cell size: {self.cell_size}, shape: {self.shape}"

    def __eq__(self, other):
        return self.grid == other.grid and self.kernel == other.kernel and self.cell_size == other.cell_size


if __name__ == '__main__':
    data_dict = {
        'geometry': [Point(1, 2), Point(2, 3), Point(3, 3)],
        'pop1': [1, 2, 3],
        'pop2': [0, 1, 1],
    }
    data = gpd.GeoDataFrame.from_dict(data_dict)
    kern = QuarticKernel(bandwidth=1.2)
    kde = KDESurface(data, 'pop1', kern, cell_size=0.1)
    plt.plot(*kde.polygon.exterior.xy)
    plt.matshow(kde.grid)
    plt.show()
