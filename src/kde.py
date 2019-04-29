import datetime
import os
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import kernel_functions, data, plotting
from .exceptions import SpatSegTypeError, SpatSegValueError, SpatSegIOError, SpatSegKeyError, SpatSegIndexError


########################################################################################################################


KERNELS = kernel_functions.KERNELS


class KernelDensitySurface:
    def __init__(
            self,
            df: pd.DataFrame,
            groups: tuple =("host", "other"),
            cell_size=25,
            kernel: str = 'biweight',
            bw=50,
            a=1,
            convex_hull=False,
            convex_hull_buffer=0,
    ):
        """
        Creates a data frame representing KDE surface clipped to minimum convex polygon of input data points.
        :param groups: population groups to be compared
        :param convex_hull_buffer: buffer around convex hull, meters
        :param convex_hull: Whether or not to use convex hull to clip kde surface
        :param df: input data with x and y coordinates representing points
        :param cell_size: cell size in meters, default 15
        :param kernel: kernel type, default 'biweight'
        :param bw: bandwidth in meters
        :param a: second parameter for biweight kernel, default 1
        :return: data frame with columns x, y and groups
        """
        self.data = df
        self.bw = bw
        self.a = a
        self.kernel = kernel
        self.cell_size = cell_size
        self.groups = list(groups)
        self.convex_hull = convex_hull
        self.convex_hull_buffer = convex_hull_buffer

        ymax, ymin = data.get_limits(df, 'y')
        xmax, xmin = data.get_limits(df, 'x')
        self.ymax = ymax + self.bw
        self.ymin = ymin - self.bw
        self.xmax = xmax + self.bw
        self.xmin = xmin - self.bw

        x = np.arange(self.xmin, self.xmax, self.cell_size)
        y = np.arange(self.ymin, self.ymax, self.cell_size)
        y = np.flipud(y)
        self.x, self.y = np.meshgrid(x, y)

        flat = self.x.flatten()[:, np.newaxis], self.y.flatten()[:, np.newaxis]
        self._data_frame = pd.DataFrame(np.hstack(flat), columns=list('xy'))

        self.d = calc_d(df, self._data_frame)
        self.w = calc_w(self.d, self.kernel, self.bw, self.a)

        for group in self.groups:
            pop = np.broadcast_to(df[group][np.newaxis:, ], self.w.shape) * self.w
            self._data_frame[group] = pd.Series(np.sum(pop, axis=1), index=self._data_frame.index)

        # if convex_hull:
        #     mcp = get_convex_hull(df, self.convex_hull_buffer)
        #     self._data_frame = select_by_location(self._data_frame, mcp)

    def __str__(self):
        return (
            "KDE surface (bandwidth={0}, "
            "cell size={1}, "
            "kernel={2})".format(
                self.bw,
                self.cell_size,
                self.kernel
            )
        )

    def __getitem__(self, item):
        try:
            col = self._data_frame[item]
            return col.values.reshape(self.shape)
        except KeyError:
            raise SpatSegKeyError
        except TypeError:
            raise SpatSegTypeError

    @property
    def size(self):
        return self.x.size

    @property
    def shape(self):
        return self.x.shape

    @property
    def values(self):
        return self._data_frame.values

    @property
    def population_values(self):
        return self._data_frame[self.groups].values

    @property
    def population_matrices(self):
        return [self._data_frame[g].values.reshape(self.shape)
                for g in self.groups]

    @property
    def coordinates(self):
        return self._data_frame[list('xy')]

    @property
    def max(self):
        return np.nanmax(self.population_values, axis=1)

    @property
    def min(self):
        return np.nanmin(self.population_values, axis=1)

    @property
    def flat(self):
        return self._data_frame

    @property
    def param(self):
        return dict(
            bw=self.bw,
            alpha=self.a,
            kernel=self.kernel,
            cell_size=self.cell_size,
            convex_hull=self.convex_hull,
            convex_hull_buffer=self.convex_hull_buffer
        )

    def iter_points(self):
        return self._data_frame.loc[:, list('xy')].itertuples()

    def normalize(self):
        pop = self.population_values
        pop /= np.nansum(pop, axis=0, keepdims=True)
        self._data_frame = pd.DataFrame(np.hstack((self.coordinates.values, pop)), columns=list('xy') + self.groups)

    def save(self, file=None):
        if not file:
            file = "KDE_{0}".format(datetime.date.today())
        try:
            self._data_frame.to_csv(file)
        except IOError:
            raise SpatSegIOError("Error! Saving failed.")

    def load(self, file=None):
        if not file:
            file = "KDE_{0}".format(datetime.date.today())
        try:
            self._data_frame = pd.DataFrame.from_csv(file)
        except SpatSegIOError:
            raise SpatSegIOError("File not found")


########################################################################################################################


# def create_kde_surface(df,
#                        cell_size=15,
#                        kernel='biweight',
#                        bw=50,
#                        a=1,
#                        convex_hull=True,
#                        convex_hull_buffer=0):
#     """
#     Creates a data frame representing kde surface clipped to minimum convex polygon of input data points.
#     :param convex_hull_buffer: buffer around convex hull, meters
#     :param convex_hull: Whether or not to use convex hull to clip kde surface
#     :param df: input data with x and y coordinates representing points
#     :param cell_size: cell size in meters, default 15
#     :param kernel: kernel type, default 'biweight'
#     :param bw: bandwidth in meters, default 50
#     :param a: second parameter for biweight kernel, default 1
#     :return: data frame with columns x, y, host and other
#     """
#
#     ymax, ymin = data.get_limits(df, 'y')
#     xmax, xmin = data.get_limits(df, 'x')
#     ymax += bw
#     ymin -= bw
#     xmax += bw
#     xmin -= bw
#     x = np.arange(xmin, xmax, cell_size)
#     y = np.arange(ymin, ymax, cell_size)
#     xx, yy = np.meshgrid(x, y)
#
#     flatten_ = xx.flatten()[:,np.newaxis], yy.flatten()[:,np.newaxis]
#     _data_frame = pd.DataFrame(np.hstack(flatten_), columns=list('xy'))
#
#     if convex_hull:
#         mcp = get_convex_hull(df, convex_hull_buffer)
#         _data_frame = select_by_location(_data_frame, mcp)
#
#     d = calc_d(df, _data_frame)
#     w = calc_w(d, kernel, bw, a)
#
#     for group in 'host', 'other':
#         pop = np.broadcast_to(df[group][np.newaxis:, ], w.shape) * w
#         _data_frame[group] = pd.Series(np.sum(pop, axis=1), index=_data_frame.index)
#
#     return _data_frame


def calc_d(d_a, d_b):
    """
    Calculates distance matrix between two sets of points.
    :param d_a: first points, data frame
    :param d_b: second points, data frame
    :return: matrix of distances between points
    """
    y_a = d_a.loc[:, 'y'].values
    x_a = d_a.loc[:, 'x'].values
    y_b = d_b.loc[:, 'y'].values
    x_b = d_b.loc[:, 'x'].values

    if y_a.shape != x_a.shape or y_b.shape != x_b.shape:
        raise SpatSegValueError("Mismatching coordinates")

    y1, y2 = tuple(np.meshgrid(y_a, y_b))
    x1, x2 = tuple(np.meshgrid(x_a, x_b))

    x_delta = x1 - x2
    y_delta = y1 - y2
    d = np.sqrt(x_delta ** 2 + y_delta ** 2)
    return d


def calc_w(d, kernel='biweight', bw=2.5, a=1):
    """
    Calculates relative weights based on distance and kernel function.
    :param d: matrix of distances
    :param kernel: kernel function to be used, default 'biweight'
    :param bw: either kernel bandwidth in meters
    :param a: second parameter for biweight kernel, default 1
    :return: matrix of relative weights w
    """
    if kernel not in KERNELS:
        raise SpatSegKeyError("Kernel not found")

    if kernel == 'biweight':
        w = KERNELS[kernel](d, bw, a)
    else:
        w = KERNELS[kernel](d, bw)

    return w


if __name__ == '__main__':
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    os.chdir(os.path.join(os.path.abspath(os.path.pardir), data.DATA_DIR))

    v80 = data.aggregate_sum(data.reform(pd.read_csv('1880.csv')))
    v00 = data.aggregate_sum(data.reform(pd.read_csv('1900.csv')))
    v20 = data.aggregate_sum(data.reform(pd.read_csv('1920.csv')))

    pop_data = {
        '1880': v80,
        '1900': v00,
        '1920': v20
    }

    with open('points1878.geojson') as f:
        point_data = json.load(f)

    d = data.add_coordinates(pop_data['1920'], point_data)
    kde = KernelDensitySurface(d, kernel='biweight', cell_size=50, bw=100)
    plotting.plot_density(kde, group='host')
    plt.show()
    plotting.plot_density(kde, group='other')
    plt.show()
    plotting.plot_diff(kde)
    plt.show()
