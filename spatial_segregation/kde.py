import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from spatial_segregation import kernel_functions, data


########################################################################################################################


class KernelDensitySurface:
    def __init__(self,
                 df,
                 groups=("host", "other"),
                 cell_size=15,
                 kernel='distance_decay',
                 bw='silverman',
                 a=1,
                 convex_hull=True,
                 convex_hull_buffer=0):
        """
        Creates a data frame representing KDE surface clipped to minimum convex polygon of input data points.
        :param groups: population groups to be compared
        :param convex_hull_buffer: buffer around convex hull, meters
        :param convex_hull: Whether or not to use convex hull to clip kde surface
        :param df: input data with x and y coordinates representing points
        :param cell_size: cell size in meters, default 15
        :param kernel: kernel type, default 'distance_decay'
        :param bw: bandwidth in meters OR method of calculating bandwidth (default 'silverman')
        :param a: second parameter for biweight kernel, default 1
        :return: data frame with columns x, y and groups
        """
        self.bw = bw
        self.a = a
        self.kernel = kernel
        self.cell_size = cell_size
        self.groups = list(groups)
        self.convex_hull_buffer = convex_hull_buffer * self.bw

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

        # TODO change to mask
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
        except IndexError as ie:
            print("IndexError!")
            raise ie
        except TypeError as te:
            print("Key is of wrong type!")
            raise te
        except Exception as e:
            print("Something went wrong")
            raise e

    @property
    def n_cells(self):
        return self.shape[0] * self.shape[1]

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
        return [self._data_frame[g].values.reshape(self.shape) for g in self.groups]

    @property
    def coordinates(self):
        return self._data_frame[:, list('xy')]

    @property
    def max(self):
        return np.nanmax(self.population_values, axis=1)

    @property
    def min(self):
        return np.nanmin(self.population_values, axis=1)

    @property
    def flat(self):
        return self._data_frame

    def iter_points(self):
        return self._data_frame.loc[:, list('xy')].itertuples()

    def plot(self):
        size = self._data_frame['host'] + self._data_frame['other']
        proportion = self._data_frame['other'] / size
        fig = self._data_frame.plot.scatter(x='x', y='y', s=size, c=proportion)
        fig.set_title("KDE surface")
        return fig

    def save(self, file=None):
        if not file:
            file = "KDE_{0}".format(datetime.date.today())
        try:
            self._data_frame.to_csv(file)
        except IOError:
            print("Error! Saving failed.")

    def load(self, file=None):
        if not file:
            file = "KDE_{0}".format(datetime.date.today())
        try:
            self._data_frame = pd.DataFrame.from_csv(file)
        except IOError:
            print("File not found")


########################################################################################################################


# def create_kde_surface(df,
#                        cell_size=15,
#                        kernel='distance_decay',
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
#     :param kernel: kernel type, default 'distance_decay'
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

    y1, y2 = tuple(np.meshgrid(y_a, y_b))
    x1, x2 = tuple(np.meshgrid(x_a, x_b))

    x_delta = x1 - x2
    y_delta = y1 - y2
    d = np.sqrt(x_delta ** 2 + y_delta ** 2)
    return d


def calc_w(d, kernel='distance_decay', bw='silverman', a=1):
    """
    Calculates relative weights based on distance and kernel function.
    :param d: matrix of distances
    :param kernel: kernel function to be used, default 'distance_decay'
    :param bw: either kernel bandwidth in meters OR method in ('silverman', 'scott'), default silverman
    :param bw: int OR str
    :param a: second parameter for biweight kernel, default 1
    :return: matrix of relative weights w
    """
    if kernel not in kernel_functions.KERNELS:
        raise ValueError("Kernel not found")

    n = d.size
    if bw == 'silverman':
        bw = round((4 * n / 4) ** (-1 / 6), 0)
    elif bw == 'scott':
        bw = round(n ** (-1/6), 0)

    if kernel == 'distance_decay':
        for x in np.nditer(d, op_flags=['readwrite']):
            x[...] = kernel_functions.KERNELS[kernel](x, bw, a)
    else:
        for x in np.nditer(d, op_flags=['readwrite']):
            x[...] = kernel_functions.KERNELS[kernel](x, bw)

    return d


if __name__ == '__main__':
    data2 = pd.DataFrame(np.ones((2, 4)), columns='x y host other'.split())
