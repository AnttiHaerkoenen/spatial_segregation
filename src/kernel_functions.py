import numpy as np
import pandas as pd

from src.exceptions import SSValueError, SSTypeError


def epanechnikov(d, bw):
    """
    Epanechnikov kernel, after Epanechnikov 1969
    :param d: distance between points, np.ndarray or pd.DataFrame
    :param bw: kernel bandwidth
    :return: weight of points, np.ndarray or pd.DataFrame
    """
    if not (isinstance(d, np.ndarray) or isinstance(d, pd.DataFrame)):
        raise SSTypeError("Data must be numpy-array or pandas DataFrame")
    if bw <= 0:
        raise SSValueError("Not a proper bandwidth")

    a = d.copy()
    i = a < bw
    a = 0.75 * (1 - (a / bw) ** 2)
    a[~i] = 0
    return a


def triangle(d, bw):
    """
    Triangle-shaped kernel
    :param d: distance between points, np.ndarray or pd.DataFrame
    :param bw: kernel bandwidth
    :return: weight of points, np.ndarray or pd.DataFrame
    """
    if not (isinstance(d, np.ndarray) or isinstance(d, pd.DataFrame)):
        raise SSTypeError("Data must be numpy-array or pandas DataFrame")
    if bw <= 0:
        raise SSValueError("Not a proper bandwidth")

    a = d.copy()
    i = a < bw
    a = 1 - a / bw
    a[~i] = 0
    return a


def gaussian(d, sigma):
    """
    Gaussian kernel function.
    :param d: distance between points, np.ndarray or pd.DataFrame
    :param sigma: kernel bandwidth
    :return: weight of points, np.ndarray or pd.DataFrame
    """
    if not (isinstance(d, np.ndarray) or isinstance(d, pd.DataFrame)):
        raise SSTypeError("Data must be numpy-array or pandas DataFrame")
    if sigma <= 0:
        raise SSValueError("Not a proper bandwidth")

    return 1 / (np.sqrt(2 * np.pi) * sigma ** 2) * np.exp(- d ** 2 / (2 * sigma ** 2))


def biweight(d, bw, alpha=1):
    """
    Distance decay function. See e. g. Martin et al. 2000
    :param d: distance between points, np.ndarray or pd.DataFrame
    :param bw: kernel bandwidth
    :param alpha: shape parameter alpha
    :return: weight of points, np.ndarray or pd.DataFrame
    """
    if not (isinstance(d, np.ndarray) or isinstance(d, pd.DataFrame)):
        raise SSTypeError("Data must be numpy-array or pandas DataFrame")
    if bw <= 0:
        raise SSValueError("Not a proper bandwidth")
    if alpha <= 0:
        raise SSValueError("Not a proper alpha")

    a = d.copy()
    i = a < bw
    a = ((bw ** 2 - a ** 2) / (bw ** 2 + a ** 2)) ** alpha
    a[~i] = 0
    return a


def uniform(d, bw):
    """
    Top hat (uniform) kernel
    :param d: distance between points, np.ndarray or pd.DataFrame
    :param bw: kernel bandwidth
    :return: weight of points, np.ndarray or pd.DataFrame
    """
    if not (isinstance(d, np.ndarray) or isinstance(d, pd.DataFrame)):
        raise SSTypeError("Data must be numpy-array or pandas DataFrame")
    if bw <= 0:
        raise SSValueError("Not a proper bandwidth")

    a = d.copy()
    i = a < bw
    a = np.ones_like(a) / bw
    a[~i] = 0
    return a


KERNELS = dict(
    biweight=biweight,
    gaussian=gaussian,
    uniform=uniform,
    epanechnikov=epanechnikov,
    triangle=triangle
)


if __name__ == '__main__':
    a = np.arange(12).reshape((3, 4))
    for f in KERNELS.values():
        print(f(a, 9))
