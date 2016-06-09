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
    :return:
    """
    pop = host + other
    total = pop.sum()
    p_n = pop / total
    index = 0

    for g in host, other:
        # TODO
        pass

    return index

def hpg(host: np.ndarray, other: np.ndarray):
    """
    Spatial exposure index. Needs two matrices of the same size.
    :param host: host group
    :param other: other group
    :return:
    """
    pass


def gini(host: np.ndarray, other: np.ndarray):
    """
    Spatial Gini index. Needs two matrices of the same size.
    :param host: host group
    :param other: other group
    :return:
    """
    pop = host + other
    p = np.nan_to_num(host / pop).ravel().tolist()
    lorenz = cum_sum(p)
    m = sum(p) / len([p[i] for i in range(len(p)) if p[i] > 0])
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
    print(h.sum())
    print(o.sum())
    print(host_share(h, o))
    print(km(h, o))
    print(hpg(h, o))
    print(gini(h, o))


if __name__ == '__main__':
    main()