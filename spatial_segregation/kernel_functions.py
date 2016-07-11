def distance_decay(d, bw, a=1):
    """
    Distance decay function. See e. g. Martin et al. 2000
    :param d: actual distance between points
    :param bw: kernel parameters bandwidth
    :param a: shape parameter alpha
    :return: weight of a point
    """

    if d < bw:
        w = ((bw ** 2 - d ** 2) / (bw ** 2 + d ** 2)) ** a
    else:
        w = 0

    return w
