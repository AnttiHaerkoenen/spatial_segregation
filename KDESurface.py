import kernel_functions as kf
import numpy as np

all_kernel_funcs = {
    'distance_decay': kf.distance_decay
}


class KDESurface:
    def __init__(self, data, cell_size, kernel, **kernel_param):
        self.kernel = all_kernel_funcs[kernel]
        self.kernel_param = kernel_param
        self.cell_size = cell_size

        self.y_max, self.y_min = data.get_y_limits()
        self.x_max, self.x_min = data.get_x_limits()

        self.y_dim = np.ceil((self.y_max - self.y_min) / self.cell_size, np.int)
        self.x_dim = np.ceil((self.x_max - self.x_min) / self.cell_size, np.int)

        self.x = np.asmatrix([[self.x_min + i * self.cell_size] * self.y_dim for i in range(self.x_dim)]).transpose()
        self.y = np.flipud(np.asmatrix([[self.y_min + i * cell_size] * self.y_dim for i in range(self.x_dim)]))

        self.host = np.zeros(self.y_dim, self.x_dim)
        self.other = np.zeros_like(self.host)

        for n in range(self.y_dim * self.x_dim):
            i, j = divmod(n, self.y_dim)
            for point in data:
                d = ((point['x'] - self.x[i][j]) ** 2 + (point['y'] - self.y[i][j])) ** 0.5
                self.host[i][j] += point['host'] * self.kernel(d, self.kernel_param)
                self.other[i][j] += point['other'] * self.kernel(d, self.kernel_param)

    def __str__(self):
        return "Kernel Density Estimated Surface, size [{}x{}]".format(self.y_dim, self.x_dim)

    def __add__(self, other):
        self.host += other.host
        self.other += other.other

    def __sub__(self, other):
        self.host -= other.host
        self.other -= other.other

    def __len__(self):
        return self.y_dim * self.x_dim

    def __eq__(self, other):
        return self.x == other.x \
               and self.y == other.y \
               and self.host == other.host \
               and self.other == other.other

    @property
    def size(self):
        return self.y_dim, self.x_dim

########################################################################################################################


def main():
    x_min, y_min = 10, 10
    x_dim, y_dim = 10, 10
    cell_size = 5
    print(np.asmatrix([[x_min + i * cell_size] * y_dim for i in range(x_dim)]).transpose())
    print(np.flipud(np.asmatrix([[y_min + i * cell_size] * y_dim for i in range(x_dim)])))


if __name__ == '__main__':
    main()
