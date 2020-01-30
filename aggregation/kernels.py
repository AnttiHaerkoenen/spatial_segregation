import numpy as np


class Kernel:
    pass


class Box(Kernel):
    classname = 'box'

    def __init__(self, bandwidth):
        self.bandwidth = bandwidth

    def __call__(self, u):
        return np.where(np.abs(u) <= self.bandwidth, 1, 0)

    def __str__(self):
        return f"box(bandwidth={self.bandwidth})"


class Martin(Kernel):
    classname = 'Martin_et_al_2000'

    def __init__(self, bandwidth, alpha=1):
        self.bandwidth = bandwidth
        self.alpha = alpha

    def __call__(self, u):
        return np.where(
            np.abs(u) <= self.bandwidth,
            ((self.bandwidth ** 2 - u ** 2) / (self.bandwidth ** 2 + u ** 2)) ** self.alpha,
            0
        )

    def __str__(self):
        return f"biweight(bandwidth={self.bandwidth},alpha={self.alpha})"


class Quartic(Kernel):
    classname = 'quartic'

    def __init__(self, bandwidth):
        self.bandwidth = bandwidth
        self._c = 3 / (np.pi * self.bandwidth * self.bandwidth)

    def __call__(self, u):
        return np.where(
            np.abs(u) <= self.bandwidth,
            self._c * (1 - (u / self.bandwidth) ** 2) ** 2,
            0
        )

    def __str__(self):
        return f"quartic(bandwidth={self.bandwidth})"


class Triangle(Kernel):
    classname = 'triangle'

    def __init__(self, bandwidth):
        self.bandwidth = bandwidth

    def __call__(self, u):
        return np.where(np.abs(u) <= self.bandwidth, 1 - u / self.bandwidth, 0)

    def __str__(self):
        return f"triangle(bandwidth={self.bandwidth})"


if __name__ == '__main__':
    pass
