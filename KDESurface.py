import kernel_functions as kf

all_kernel_funcs = {
    'distance_decay': kf.distance_decay
}


class KDESurface:
    def __init__(self, data, kernel, **kernel_param):
        self._data = data
        self._kernel = all_kernel_funcs[kernel]
        self._param = kernel_param

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


def main():
    pass


if __name__ == '__main__':
    main()