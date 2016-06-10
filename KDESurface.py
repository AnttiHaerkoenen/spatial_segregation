import kernel_functions as kf
import numpy as np

all_kernel_funcs = {
    'distance_decay': kf.distance_decay
}


class KDESurface:
    def __init__(self, data, cell_size, kernel, **kernel_param):
        self._kernel = all_kernel_funcs[kernel]
        self._param = kernel_param
        self.cell_size = cell_size

        self.y_max, self.y_min = data.get_y_limits()
        self.x_max, self.x_min = data.get_x_limits()

        # TODO self.x
        # TODO self.y
        # TODO self.host
        # TODO self.other

    def __str__(self):
        pass

    def __add__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __mul__(self, other):
        pass

    def __len__(self):
        pass

########################################################################################################################


def main():
    pass


if __name__ == '__main__':
    main()