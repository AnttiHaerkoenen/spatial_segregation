import numpy as np


def epanechnikov(d, bw):
    """
    Epanechnikov kernel, after Epanechnikov 1969
    :param d: distance between points
    :param bw: kernel bandwidth
    :return: weight of a point
    """
    # if d < bw:
    #     return 0.75 * (1 - (d / bw) ** 2)
    # else:
    #     return 0
    a = d.copy()
    i = a < bw
    a = 0.75 * (1 - (a / bw) ** 2)
    a[~i] = 0
    return a


def triangle(d, bw):
    """
    Triangle-shaped kernel
    :param d: distance between points
    :param bw: kernel bandwidth
    :return: weight of a point
    """
    # if d < bw:
    #     return 1 - d / bw
    # else:
    #     return 0
    a = d.copy()
    i = a < bw
    a = 1 - a / bw
    a[~i] = 0
    return a


def gaussian(d, sigma):
    """
    Gaussian kernel function.
    :param d: distance between points
    :param sigma: kernel bandwidth
    :return: weight of a point
    """
    return 1 / (np.sqrt(2 * np.pi) * sigma ** 2) * np.exp(- d ** 2 / (2 * sigma ** 2))


def distance_decay(d, bw, alpha=1):
    """
    Distance decay function. See e. g. Martin et al. 2000
    :param d: distance between points
    :param bw: kernel bandwidth
    :param alpha: shape parameter alpha
    :return: weight of a point
    """
    a = d.copy()
    i = a < bw
    a = ((bw ** 2 - a ** 2) / (bw ** 2 + a ** 2)) ** alpha
    a[~i] = 0
    return a


def uniform(d, bw):
    """
    Top hat (uniform) kernel
    :param d: distance between points
    :param bw: kernel bandwidth
    :return: weight of a point
    """
    a = d.copy()
    i = a < bw
    a = np.ones_like(a) / bw
    a[~i] = 0
    return a
    # return 1/bw if d < bw else 0


KERNELS = dict(
    distance_decay=distance_decay,
    gaussian=gaussian,
    uniform=uniform,
    epanechnikov=epanechnikov,
    triangle=triangle
)


if __name__ == '__main__':
    a = np.arange(12).reshape((3, 4))
    for f in KERNELS.values():
        print(f(a, 9))
