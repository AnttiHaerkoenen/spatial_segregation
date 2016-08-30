import numpy as np
import pandas as pd
import shapely.geometry

from spatial_segregation import kernel_functions, data

kernel_dict = {
    'distance_decay': kernel_functions.distance_decay
}


def create_kde_surface(df, cell_size=15, kernel='distance_decay', bw=500, a=1):
    ymax, ymin = data.get_y_limits(df)
    xmax, xmin = data.get_x_limits(df)
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

    mcp = get_convex_hull(df)

    d_dict = select_by_location(d_dict, mcp)

    d = calc_d(df, d_dict)
    w = calc_w(d, kernel, bw, a)

    for group in 'host', 'other':
        pop = np.broadcast_to(df[group][np.newaxis:, ], w.shape) * w
        d_dict[group] = np.sum(pop, axis=1)

    return pd.DataFrame(d_dict)


def calc_d(d_a, d_b):
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


def calc_w(d, kernel='distance_decay', bw=10, a=1):
    if kernel not in kernel_dict:
        raise ValueError("Kernel not found")

    for x in np.nditer(d, op_flags=['readwrite']):
        x[...] = kernel_dict[kernel](x, bw, a)

    return d


def select_by_location(xy_dict, polygon):
    xx = xy_dict['x']
    yy = xy_dict['y']
    xy = []

    for i in range(len(xx)):
        xy.append((xx[i], yy[i]))

    points = [p for p in xy if polygon.contains(shapely.geometry.Point(p))]

    x = [p(0) for p in points]
    y = [p(1) for p in points]

    return {
        'x': np.array(x),
        'y': np.array(y)
    }


def get_convex_hull(data):
    x = data['x']
    y = data['y']
    xy = []

    for i in range(len(x)):
        xy.append((x[i], y[i]))

    convex_hull = shapely.geometry.MultiPoint(xy).convex_hull

    return convex_hull


def main():
    data2 = pd.DataFrame(np.ones((2, 4)), columns='x y host other'.split())
    create_kde_surface(data2)


if __name__ == '__main__':
    main()
