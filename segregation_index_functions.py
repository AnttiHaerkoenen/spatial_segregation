import numpy as np


def host_share(host: np.ndarray, other: np.ndarray):
    """
    Calculates host share. Needs two matrices of the same size.
    :param host: host group
    :param other: other group
    :return: host share
    """
    return host.sum() / (host.sum() + other.sum())


def km(host: np.ndarray, other: np.ndarray):
    """
    Karmel-MacLachlan index of segregation. Needs two matrices of the same size.
    :param host: host group
    :param other: other group
    :return: km index
    """
    index = 0
    pop = host + other
    total = pop.sum()
    p_n = pop / total
    y_dim, x_dim = host.shape

    for g in host, other:
        index_g = 0
        p_g = g.sum() / total

        for i in range(y_dim):
            for j in range(x_dim):
                p_gn = np.nan_to_num(g[i][j] / total)
                index_gn = p_n[i][j] * abs(np.nan_to_num(p_gn / (p_g * p_n[i][j]) - 1))
                index_g += index_gn

        index += index_g * p_g

    return index


def hpg(host: np.ndarray, other: np.ndarray):
    """
    Spatial exposure index. Needs two matrices of the same size.
    :param host: host group
    :param other: other group
    :return: spatial exposure index
    """
    index = 0
    t_n = host + other
    t_h = host.sum()
    y_dim, x_dim = host.shape

    for i in range(y_dim):
        for j in range(x_dim):
            p_gn = np.nan_to_num(other[i][j] / t_n[i][j])
            index += p_gn * host[i][j] / t_h

    return index


def gini(host: np.ndarray, other: np.ndarray):
    """
    Spatial Gini index. Needs two matrices of the same size.
    :param host: host group
    :param other: other group
    :return: spatial gini index
    """
    pop = host + other
    p = np.nan_to_num(host / pop).ravel().tolist()
    lorenz = cum_sum(p)

    m = sum(p) / len(
        [p[i] for i in range(len(p)) if p[i] > 0])

    equal = [m * (i + 1) for i in range(len(lorenz))]

    return (sum(equal) - sum(lorenz)) / sum(equal)


def cum_sum(x):
    """
    Calculates cumulative sum
    :param x: list of values
    :return: list of cumulative values
    """
    x = [n for n in x if n > 0]
    x.sort()

    result = [x[0]]

    for n in x[1:]:
        result.append(n + result[-1])

    return result

########################################################################################################################


def main():
    h, o = np.random.rand(10, 12), np.random.rand(10, 12)
    print("host share: ", host_share(h, o))
    print("km: ", km(h, o))
    print("hpg: ", hpg(h, o))
    print("gini: ", gini(h, o))


if __name__ == '__main__':
    main()