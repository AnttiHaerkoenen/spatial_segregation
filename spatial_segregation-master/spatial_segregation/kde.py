import numpy as np
from statsmodels.nonparametric.kernel_density import KDEMultivariate


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

        self.x = np.broadcast_to(np.arange(self._x_min, self._x_max, self.cell_size), (self._y_dim, self._x_dim))

        self.y = np.broadcast_to(np.flipud(np.arange(self._y_min, self._y_max, self.cell_size)),
                                 (self._x_dim, self._y_dim)).T

        self.host = self._compute_kernels('host')
        self.other = self._compute_kernels('other')

    def _compute_kernels(self, group):
        pass

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
    x_min, y_min = 10, 10
    x_dim, y_dim = 10, 10
    cell_size = 10
    print(np.asmatrix([[x_min + i * cell_size] * y_dim for i in range(x_dim)]).transpose())
    print(np.flipud(np.asmatrix([[y_min + i * cell_size] * y_dim for i in range(x_dim)])))


if __name__ == '__main__':
    main()
