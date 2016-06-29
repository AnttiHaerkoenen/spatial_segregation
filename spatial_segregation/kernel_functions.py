def distance_decay(d, param):
    """
    Distance decay function. See e. g. Martin et al. 2000
    :param d: actual distance between points
    :param param: kernel parameters
    :return: weight of point
    """
    bw = param['bw']
    a = param['a']

    if d < bw:
        w = ((bw ** 2 - d ** 2) / (bw ** 2 + d ** 2)) ** a
    else:
        w = 0

    return w
