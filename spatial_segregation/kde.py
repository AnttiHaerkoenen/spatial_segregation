import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import shapely.geometry

from spatial_segregation import kernel_functions, data

kernel_dict = {
    'distance_decay': kernel_functions.distance_decay,
    'uniform': kernel_functions.uniform
}

########################################################################################################################


class KernelDensitySurface:
    def __init__(self,
                 df,
                 groups=("host", "other"),
                 cell_size=15,
                 kernel='distance_decay',
                 bw=50,
                 a=1,
                 convex_hull=True,
                 convex_hull_buffer=0):
        """
        Creates a data frame representing kde surface clipped to minimum convex polygon of input data points.
        :param groups: population groups to be compared
        :param convex_hull_buffer: buffer around convex hull, meters
        :param convex_hull: Whether or not to use convex hull to clip kde surface
        :param df: input data with x and y coordinates representing points
        :param cell_size: cell size in meters, default 15
        :param kernel: kernel type, default 'distance_decay'
        :param bw: bandwidth in meters, default 50
        :param a: second parameter for biweight kernel, default 1
        :return: data frame with columns x, y and groups
        """
        self.bw = bw
        self.a = a
        self.kernel = kernel
        self.cell_size = cell_size
        self.groups = groups

        ymax, ymin = data.get_limits(df, 'y')
        xmax, xmin = data.get_limits(df, 'x')
        self.ymax = ymax + self.bw
        self.ymin = ymin - self.bw
        self.xmax = xmax + self.bw
        self.xmin = xmin - self.bw
        print(self.ymax, self.ymin, self.xmax, self.xmin, self.cell_size)

        x = np.arange(self.xmin, self.xmax, self.cell_size)
        y = np.arange(self.ymin, self.ymax, self.cell_size)
        xx, yy = np.meshgrid(x, y)

        flat = xx.flatten()[:,np.newaxis], yy.flatten()[:,np.newaxis]
        self.data_frame = pd.DataFrame(np.hstack(flat), columns=list('xy'))

        if convex_hull:
            mcp = get_convex_hull(df, convex_hull_buffer)
            self.data_frame = select_by_location(self.data_frame, mcp)

        self.d = calc_d(df, self.data_frame)
        self.w = calc_w(self.d, self.kernel, self.bw, self.a)

        for group in self.groups:
            pop = np.broadcast_to(df[group][np.newaxis:, ], self.w.shape) * self.w
            self.data_frame[group] = pd.Series(np.sum(pop, axis=1), index=self.data_frame.index)

    def __str__(self):
        return(
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
            self.data_frame[item]
        except IndexError as e:
            print("IndexError!")
            raise e
        except TypeError as e:
            print("Key is of wrong type!")
            raise e

    @property
    def values(self):
        return self.data_frame.values

    @property
    def population_values(self):
        return self.data_frame.isin(self.groups).values

    def plot(self, style='classic'):
        plt.style.use(style)

        size = self.data_frame['host'] + self.data_frame['other']
        proportion = self.data_frame['other'] / size
        self.data_frame.plot.scatter(x='x', y='y', s=size, c=proportion)
        plt.title("KDE surface")
        plt.show()

    def save(self, file=None):
        if not file:
            file = "KDE {0}".format(datetime.datetime.today())
        try:
            self.data_frame.to_csv(file)
        except IOError:
            print("Error! Saving failed.")

    def load(self, file=None):
        if not file:
            file = "KDE {0}".format(datetime.datetime.today())
        try:
            self.data_frame = pd.DataFrame.from_csv(file)
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
#     data_frame = pd.DataFrame(np.hstack(flatten_), columns=list('xy'))
#
#     if convex_hull:
#         mcp = get_convex_hull(df, convex_hull_buffer)
#         data_frame = select_by_location(data_frame, mcp)
#
#     d = calc_d(df, data_frame)
#     w = calc_w(d, kernel, bw, a)
#
#     for group in 'host', 'other':
#         pop = np.broadcast_to(df[group][np.newaxis:, ], w.shape) * w
#         data_frame[group] = pd.Series(np.sum(pop, axis=1), index=data_frame.index)
#
#     return data_frame


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


def calc_w(d, kernel='distance_decay', bw=100, a=1):
    """
    Calculates relative weights based on distance and kernel function.
    :param d: matrix of distances
    :param kernel: kernel function to be used, default 'distance_decay'
    :param bw: kernel bandwidth in meters, default 100
    :param a: second parameter for biweight kernel, default 1
    :return: matrix of relative weights w
    """
    if kernel not in kernel_dict:
        raise ValueError("Kernel not found")

    if kernel == 'distance_decay':
        for x in np.nditer(d, op_flags=['readwrite']):
            x[...] = kernel_dict[kernel](x, bw, a)
    else:
        for x in np.nditer(d, op_flags=['readwrite']):
            x[...] = kernel_dict[kernel](x, bw)

    return d


def select_by_location(point_data, polygon):
    """
    Select points inside a polygon.
    :param point_data: data frame of coordinates
    :param polygon: instance of shapely.geometry.polygon.Polygon
    :return: data frame of coordinates
    """
    xy = [(row.x, row.y) for row in point_data.itertuples()]

    points = [p for p in xy if polygon.contains(shapely.geometry.point.Point(p[0], p[1]))]

    return pd.DataFrame(np.asarray(points), columns=list('xy'))


def get_convex_hull(point_data, convex_hull_buffer=0):
    """
    Create a convex hull based on points
    :param convex_hull_buffer: buffer around convex hull, meters
    :param point_data: data frame of coordinates
    :return: a shapely.geometry.polygon.Polygon
    """
    xy = [(row.x, row.y) for row in point_data.itertuples()]

    convex_hull = shapely.geometry.MultiPoint(xy).convex_hull

    return convex_hull.buffer(convex_hull_buffer)


def main():
    data2 = pd.DataFrame(np.ones((2, 4)), columns='x y host other'.split())


if __name__ == '__main__':
    main()
