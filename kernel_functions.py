def distance_decay(d, bw, a):
    """
    Distance decay function. See e. g. Martin et al. 2000
    :param d: actual distance between points
    :param bw: bandwidth
    :param a: alpha
    :return: weight of point
    """
    if d < bw:
        w = ((bw ** 2 - d ** 2) / (bw ** 2 + d ** 2)) ** a
    else:
        w = 0
    return w