import numpy as np


def host_share(x):
    """
    Calculates host share.

    :param x: 2-dim array with groups as columns
    :return: host share
    """
    pop = np.apply_along_axis(sum, 0, x)
    return pop[0] / sum(pop)


def km(x):
    """
    Karmel-MacLachlan index of segregation.

    :param x: 2-dim array with groups as columns
    :return: km index
    """
    index = 0
    areas, groups = x.shape
    pop = np.apply_along_axis(sum, 1, x)
    total = sum(pop)
    p_n = pop / total

    for g in np.hsplit(x, groups):
        index_g = 0
        p_g = sum(g) / total

        for k in range(areas):
            p_gn = np.nan_to_num(g[k] / total)
            index_gn = p_n[k] * abs(np.nan_to_num(p_gn / (p_g * p_n[k]) - 1))
            index_g += index_gn

        index += index_g * p_g

    return index[0]


def hpg(x, host_col=0):
    """
    Spatial exposure index.

    :param x: 2-dim array with groups as columns
    :param host_col: column of the host group
    :return: spatial exposure index
    """
    index = 0
    areas, groups = x.shape
    t_n = np.apply_along_axis(sum, 1, x)

    others = np.hsplit(x, groups)
    host = others[host_col]
    del others[host_col]
    t_h = sum(host)

    for g in others:
        for k in range(areas):
            p_gn = np.nan_to_num(g[k] / t_n[k])
            index += p_gn * host[k] / t_h

    return index[0]

########################################################################################################################


def main():
    x = np.random.rand(20, 3)
    print(x)
    print("host share: ", host_share(x))
    print("km: ", km(x))
    print("hpg: ", hpg(x))


if __name__ == '__main__':
    main()