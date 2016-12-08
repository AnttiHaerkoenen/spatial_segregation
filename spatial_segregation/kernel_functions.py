import math


def gaussian(d, bw):
    """
    Gaussian kernel function.
    :param d: distance between points
    :param bw: kernel bandwidth
    :return: weight of a point
    """
    pass  # TODO gaussian kernel


def distance_decay(d, bw, a=1):
    """
    Distance decay function. See e. g. Martin et al. 2000
    :param d: distance between points
    :param bw: kernel bandwidth
    :param a: shape parameter alpha
    :return: weight of a point
    """
    if d < bw:
        return ((bw ** 2 - d ** 2) / (bw ** 2 + d ** 2)) ** a
    else:
        return 0


def uniform(d, bw):
    """
    Top hat (uniform) kernel
    :param d: distance between points
    :param bw: kernel bandwidth
    :return: weight of a point
    """
    if d < bw:
        return 1 / (math.pi * bw ** 2)
    else:
        return 0


KERNELS = {
    'distance_decay': distance_decay,
    'gaussian': gaussian,
    'uniform': uniform
}
