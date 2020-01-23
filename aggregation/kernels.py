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


class Biweight(Kernel):
    classname = 'biweight'

    def __init__(self, bandwidth, alpha=1):
        self.bandwidth = bandwidth
        self.alpha = alpha

    def __call__(self, u):
        return np.where(
            np.abs(u) <= self.bandwidth,
            ((self.bandwidth ** 2 - u ** 2) / (self.bandwidth ** 2 + u ** 2)) ** self.alpha, 0
        )

    def __str__(self):
        return f"biweight(bandwidth={self.bandwidth},alpha={self.alpha})"


class Triangle(Kernel):
    classname = 'triangle'

    def __init__(self, bandwidth):
        self.bandwidth = bandwidth

    def __call__(self, u):
        return np.where(np.abs(u) <= self.bandwidth, 1 - u / self.bandwidth, 0)

    def __str__(self):
        return f"triangle(bandwidth={self.bandwidth})"


if __name__ == '__main__':
    gauss = Gaussian(100)
    print(gauss)
    print(gauss(np.array([100, 200, 300])))
