import numpy as np
import matplotlib.pyplot as plt


def epanechnikov(d, bw):
    """
    Epanechnikov kernel, after Epanechnikov 1969
    :param d: distance between points
    :param bw: kernel bandwidth
    :return: weight of a point
    """
    if d < bw:
        return 0.75 * (1 - (d / bw) ** 2)
    else:
        return 0


def triangle(d, bw):
    """
    Triangle-shaped kernel
    :param d: distance between points
    :param bw: kernel bandwidth
    :return: weight of a point
    """
    if d < bw:
        return 1 - d / bw
    else:
        return 0


def gaussian(d, sigma):
    """
    Gaussian kernel function.
    :param d: distance between points
    :param sigma: kernel bandwidth
    :return: weight of a point
    """
    return 1 / (np.sqrt(2 * np.pi) * sigma ** 2) * np.exp(- d ** 2 / (2 * sigma ** 2))


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
    return 1/bw if d < bw else 0


def plot_kernel(kernel, bw=1):
    """
    Function for plotting kernels.
    :param kernel: kernel function object
    :param bw: bw parameter
    :return: matplotlib.lines.Line2D object
    """
    x = np.arange(-2 * bw, 2 * bw, 0.01)
    y = [kernel(abs(x), bw) for x in np.nditer(x)]
    fig = plt.plot(x, y)
    return fig


KERNELS = dict(
    distance_decay=distance_decay,
    gaussian=gaussian,
    uniform=uniform,
    epanechnikov=epanechnikov,
    triangle=triangle
)


if __name__ == '__main__':
    plt.style.use("ggplot")

    for k, f in KERNELS.items():
        plot_kernel(f)
        # plt.title(k.capitalize())
        plt.ylim((-0.2, 1.2))
        plt.ylabel("K(d)")
        plt.xlabel("d")
        plt.show()
