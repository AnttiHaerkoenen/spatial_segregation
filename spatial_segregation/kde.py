import numpy as np
import pandas as pd
import shapely.geometry

from spatial_segregation import kernel_functions, data

kernel_dict = {
    'distance_decay': kernel_functions.distance_decay,
    'uniform': kernel_functions.uniform
}


def create_kde_surface(df,
                       cell_size=15,
                       kernel='distance_decay',
                       bw=50,
                       a=1,
                       convex_hull=True,
                       convex_hull_buffer=0):
    """
    Creates a data frame representing kde surface clipped to minimum convex polygon of input data points.
    :param convex_hull_buffer: buffer around convex hull, meters
    :param convex_hull: Whether or not to use convex hull to clip kde surface
    :param df: input data with x and y coordinates representing points
    :param cell_size: cell size in meters, default 15
    :param kernel: kernel type, default 'distance_decay'
    :param bw: bandwidth in meters, default 50
    :param a: second parameter for biweight kernel, default 1
    :return: data frame with columns x, y, host and other
    """
    ymax, ymin = data.get_limits(df, 'y')
    xmax, xmin = data.get_limits(df, 'x')
    ymax += bw
    ymin -= bw
    xmax += bw
    xmin -= bw
    x = np.arange(xmin, xmax, cell_size)
    y = np.arange(ymin, ymax, cell_size)
    xx, yy = np.meshgrid(x, y)

    flatten_ = xx.flatten()[:,np.newaxis], yy.flatten()[:,np.newaxis]
    d_frame = pd.DataFrame(np.hstack(flatten_), columns=list('xy'))

    if convex_hull:
        mcp = get_convex_hull(df, convex_hull_buffer)
        d_frame = select_by_location(d_frame, mcp)

    d = calc_d(df, d_frame)
    w = calc_w(d, kernel, bw, a)

    for group in 'host', 'other':
        pop = np.broadcast_to(df[group][np.newaxis:, ], w.shape) * w
        d_frame[group] = pd.Series(np.sum(pop, axis=1), index=d_frame.index)

    return d_frame


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
    kde = create_kde_surface(data2, convex_hull_buffer=10)


if __name__ == '__main__':
    main()
