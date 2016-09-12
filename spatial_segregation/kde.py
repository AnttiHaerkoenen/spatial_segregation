import numpy as np
import pandas as pd
import shapely.geometry

from spatial_segregation import kernel_functions, data

kernel_dict = {
    'distance_decay': kernel_functions.distance_decay
}


def create_kde_surface(df, cell_size=15, kernel='distance_decay', bw=100, a=1, convex_hull=True, convex_hull_buffer=0):
    """
    Creates a data frame representing kde surface clipped to minimum convex polygon of input data points.
    :param convex_hull_buffer: buffer around convex hull, meters
    :param convex_hull: Whether or not to use convex hull to clip kde surface
    :param df: input data with x and y coordinates representing points
    :param cell_size: cell size in meters, default 15
    :param kernel: kernel type, default 'distance_decay'
    :param bw: bandwidth in meters, default 100
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

    d_dict = {
        'x': xx.flatten(),
        'y': yy.flatten(),
    }

    if convex_hull:
        mcp = get_convex_hull(df, convex_hull_buffer)
        d_dict = select_by_location(d_dict, mcp)

    d = calc_d(df, d_dict)
    w = calc_w(d, kernel, bw, a)

    for group in 'host', 'other':
        pop = np.broadcast_to(df[group][np.newaxis:, ], w.shape) * w
        d_dict[group] = np.sum(pop, axis=1)

    return pd.DataFrame(d_dict)


def calc_d(d_a, d_b):
    """
    Calculates distance matrix between two sets of points.
    :param d_a: first points, dict of arrays
    :param d_b: second points, dict of arrays
    :return: matrix of distances between points
    """
    for df in d_a, d_b:
        if type(df) == 'pandas.core.series.Series':
            df = df.to_dict(orient='list')
            df['y'] = np.array(df['y'])
            df['x'] = np.array(df['x'])

    y_a = d_a['y']
    x_a = d_a['x']
    y_b = d_b['y']
    x_b = d_b['x']

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

    for x in np.nditer(d, op_flags=['readwrite']):
        x[...] = kernel_dict[kernel](x, bw, a)

    return d


def select_by_location(xy_dict, polygon):
    """
    Select points inside a polygon.
    :param xy_dict: dictionary of arrays of x and y
    :param polygon: instance of shapely.geometry.Polygon
    :return: dictionary of arrays of x and y
    """
    xx = xy_dict['x']
    yy = xy_dict['y']
    xy = []

    for i in range(len(xx)):
        xy.append((xx[i], yy[i]))

    points = [p for p in xy if polygon.intersects(shapely.geometry.Point(p))]

    x = [p[0] for p in points]
    y = [p[1] for p in points]

    return {
        'x': np.array(x),
        'y': np.array(y)
    }


def get_convex_hull(point_data, convex_hull_buffer=0):
    """
    Create a convex hull based on points
    :param convex_hull_buffer: buffer around convex hull, meters
    :param point_data: dict of arrays of coordinates
    :return: instance of shapely.geometry.Polygon
    """
    x = point_data['x']
    y = point_data['y']
    xy = []

    for i in range(len(x)):
        xy.append((x[i], y[i]))

    convex_hull = shapely.geometry.MultiPoint(xy).convex_hull

    return convex_hull.buffer(convex_hull_buffer)


def main():
    data2 = pd.DataFrame(np.ones((2, 4)), columns='x y host other'.split())
    kde = create_kde_surface(data2, convex_hull_buffer=10)


if __name__ == '__main__':
    main()
