import numpy as np

import spatial_segregation.kernel_functions as kf
import spatial_segregation.data


class KDESurface:
    def __init__(self, data_frame, cell_size=10, kernel='distance_decay', bw=50, a=1):
        self.kernel = kernel
        self.cell_size = cell_size
        self.bw = bw
        self.a = a

        self._y_max, self._y_min = data_frame.get_y_limits(data_frame)
        self._x_max, self._x_min = data_frame.get_x_limits(data_frame)

        self._y_max += self.bw
        self._y_min -= self.bw
        self._x_max += self.bw
        self._x_min -= self.bw

        self._y_dim = np.ceil((self._y_max - self._y_min) / self.cell_size).astype(int)
        self._x_dim = np.ceil((self._x_max - self._x_min) / self.cell_size).astype(int)

        self.x = np.tile(np.arange(self._x_min, self._x_max, self.cell_size), self._y_dim)
        self.y = np.flipud(np.repeat(np.arange(self._y_min, self._y_max, self.cell_size), self._x_dim))

        d = calc_d(self.y, self.x, data_frame.data['y'], data_frame.data['x'])
        w = calc_w(d, kernel=self.kernel, bw=self.bw)

        self.host = sum(w * data_frame.data['host'], axis=1)
        self.other = sum(w * data_frame.data['other'], axis=1)

    def __str__(self):
        return "Kernel Density Estimated Surface, size {} x {}".format(self._y_dim, self._x_dim)

    def __add__(self, other):
        self.host += other.host
        self.other += other.other

    def __sub__(self, other):
        self.host -= other.host
        self.other -= other.other

    def __len__(self):
        return len(self.x)

    @property
    def size(self):
        return self._y_dim, self._x_dim

    @property
    def y_limits(self):
        return self._y_max, self._y_min

    @property
    def x_limits(self):
        return self._x_max, self._x_min

    @property
    def y_grid(self):
        return self.y.reshape(self._y_dim, self._x_dim)

    @property
    def x_grid(self):
        return self.x.reshape(self._y_dim, self._x_dim)

    @property
    def host_grid(self):
        return self.host.reshape(self._y_dim, self._x_dim)

    @property
    def other_grid(self):
        return self.other.reshape(self._y_dim, self._x_dim)


########################################################################################################################

kernel_dict = {
    'distance_decay': kf.distance_decay
}


def calc_d(y_a, x_a, y_b, x_b):
    if (len(y_a) != len(x_a)) or (len(y_b) != len(x_b)):
        raise ValueError("Input coordinate mismatch")

    cols = len(y_b)
    y1, y2 = tuple(np.broadcast_arrays(y_a, np.reshape(y_b, (cols, 1))))
    x1, x2 = tuple(np.broadcast_arrays(x_a, np.reshape(x_b, (cols, 1))))

    return ((y1 - y2) ** 2 + (x1 - x2) ** 2) ** 0.5


def calc_w(d, kernel='distance_decay', bw=10, a=1):
    if kernel not in kernel_dict:
        raise ValueError("Kernel not found")

    func = np.vectorize(kernel_dict[kernel], excluded={'bw', 'a'})

    return func(d, bw, a)

########################################################################################################################


def main():
    pass


if __name__ == '__main__':
    main()
