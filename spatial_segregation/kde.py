import numpy as np


class KDESurface:
    def __init__(self, data, cell_size=10, kernel='distance_decay', bw=50, a=1):
        self.kernel = kernel
        self.cell_size = cell_size
        self.bw = bw
        self.a = a

        self._y_max, self._y_min = data.get_y_limits()
        self._x_max, self._x_min = data.get_x_limits()

        self._y_max += self.bw
        self._y_min -= self.bw
        self._x_max += self.bw
        self._x_min -= self.bw

        self._y_dim = np.ceil((self._y_max - self._y_min) / self.cell_size).astype(int)
        self._x_dim = np.ceil((self._x_max - self._x_min) / self.cell_size).astype(int)

        self.x = np.tile(np.arange(self._x_min, self._x_max, self.cell_size), self._y_dim)
        self.y = np.flipud(np.repeat(np.arange(self._y_min, self._y_max, self.cell_size), self._x_dim))

        self.host = None
        self.other = None

    def __str__(self):
        return "Kernel Density Estimated Surface, size {} x {}".format(self._y_dim, self._x_dim)

    def __add__(self, other):
        self.host += other.host
        self.other += other.other

    def __sub__(self, other):
        self.host -= other.host
        self.other -= other.other

    def __len__(self):
        return self._y_dim * self._x_dim

    @property
    def size(self):
        return self._y_dim, self._x_dim

    @property
    def y_limits(self):
        return self._y_max, self._y_min

    @property
    def x_limits(self):
        return self._x_max, self._x_min


########################################################################################################################


def main():
    x_min, x_max = 10, 51
    y_min, y_max = 10, 101
    x_dim, y_dim = 5, 10
    cell_size = 10
    x = np.tile(np.arange(x_min, x_max, cell_size), y_dim)
    y = np.flipud(np.repeat(np.arange(y_min, y_max, cell_size), x_dim))
    print(x, "\n", y)


if __name__ == '__main__':
    main()
