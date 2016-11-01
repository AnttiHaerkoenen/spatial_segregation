def get_stars(p):
    """
    R-style significance symbols.
    :param p: p-value
    :return: '***', '**', '*', '.' or ' '
    """
    if p < 0 or p > 1:
        raise ValueError("Impossible!")
    elif p <= 0.001:
        return "***"
    elif p <= 0.01:
        return "**"
    elif p <= 0.05:
        return "*"
    elif p <= 0.1:
        return "."
    else:
        return " "
