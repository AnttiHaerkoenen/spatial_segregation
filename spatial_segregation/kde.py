import math

import numpy as np
import pandas as pd

from spatial_segregation import kernel_functions, data

# class KDESurface:
#     def __init__(self, data_frame, cell_size=10, kernel='distance_decay', bw=50, a=1):
#         self.kernel = kernel
#         self.cell_size = cell_size
#         self.bw = bw
#         self.a = a
#
#         self._y_max, self._y_min = data.get_y_limits(data_frame)
#         self._x_max, self._x_min = data.get_x_limits(data_frame)
#
#         self._y_max += self.bw
#         self._y_min -= self.bw
#         self._x_max += self.bw
#         self._x_min -= self.bw
#
#         self._y_dim = math.ceil((self._y_max - self._y_min) / self.cell_size)
#         self._x_dim = math.ceil((self._x_max - self._x_min) / self.cell_size)
#         x = np.arange(self._x_min, self._x_max, self.cell_size)
#         y = np.arange(self._y_min, self._y_max, self.cell_size)
#         self.x, self.y = np.meshgrid(x, y)
#
#         d = calc_d(self.flat_y, self.flat_x, data_frame['y'].copy(), data_frame['x'].copy())
#         w = calc_w(d, kernel=self.kernel, bw=self.bw)
#
#         # self.host = sum(w * data_frame['host'], axis=1)
#         # self.other = sum(w * data_frame['other'], axis=1)
#
#     def __str__(self):
#         return "Kernel Density Estimated Surface, size {} x {}".format(self._y_dim, self._x_dim)
#
#     def __add__(self, other):
#         self.host += other.host
#         self.other += other.other
#
#     def __sub__(self, other):
#         self.host -= other.host
#         self.other -= other.other
#
#     def __len__(self):
#         return len(self.x)
#
#     @property
#     def size(self):
#         return self._y_dim, self._x_dim
#
#     @property
#     def y_limits(self):
#         return self._y_max, self._y_min
#
#     @property
#     def x_limits(self):
#         return self._x_max, self._x_min
#
#     @property
#     def flat_y(self):
#         return self.y.flatten()
#
#     @property
#     def flat_x(self):
#         return self.x.flatten()
#
#     @property
#     def flat_host(self):
#         return self.host.flatten()
#
#     @property
#     def flat_other(self):
#         return self.other.flatten()

kernel_dict = {
    'distance_decay': kernel_functions.distance_decay
}


def create_kde_surface(df, cell_size=10, kernel='distance_decay', bw=50, a=1):
    ymax, ymin = data.get_y_limits(df)
    xmax, xmin = data.get_x_limits(df)
    ymax += bw
    ymin -= bw
    xmax += bw
    xmin -= bw
    x = np.arange(ymin, ymax, cell_size)
    y = np.arange(xmin, xmax, cell_size)
    xx, yy = np.meshgrid(x, y)

    d_dict = {
        'x': xx.flatten(),
        'y': yy.flatten(),
    }

    d = calc_d(d_dict, df)
    w = calc_w(d, kernel, bw, a)

    for group in 'host', 'other':
        d_dict[group] = w * df[group]

    return pd.DataFrame(d_dict)


def calc_d(d_a, d_b):
    y_a = d_a['y']
    x_a = d_a['x']
    y_b = d_b['y']
    x_b = d_b['x']

    if (y_a.shape != x_a.shape) or (y_b.shape != x_b.shape):
        raise ValueError("Input coordinate mismatch")

    y1, y2 = np.meshgrid(y_a, y_b)
    x1, x2 = np.meshgrid(x_a, x_b)

    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def calc_w(d, kernel='distance_decay', bw=10, a=1):
    if kernel not in kernel_dict:
        raise ValueError("Kernel not found")

    func = np.vectorize(kernel_dict[kernel], excluded={'bw', 'a'})

    return func(d, bw, a)


def main():
    pass


if __name__ == '__main__':
    main()
