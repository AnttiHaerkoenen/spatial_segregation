from collections import namedtuple

from .exceptions import SpatSegTypeError

ParameterPermutation = namedtuple('ParameterPermutation', 'cell_size, kernel, bw, alpha')

NEEDS_ALPHA = frozenset('biweight')


class Parameters:
    def __init__(self, cell_sizes, kernels, bws, alphas):
        self.cell_sizes = set(cell_sizes)
        self.kernels = set(kernels)
        self.bws = set(bws)
        self.alphas = set(alphas)

    def __str__(self):
        return "Parameters" \
               "Kernels: {k}\n" \
               "Bandwidths: {bw}\n" \
               "Alphas: {a}\n" \
               "Cell sizes: {c}".format(k=self.kernels, bw=self.bws, a=self.alphas, c=self.cell_sizes)

    def __iter__(self):
        for c in self.cell_sizes:
            for k in self.kernels:
                for bw in self.bws:
                    if k in NEEDS_ALPHA:
                        for a in self.alphas:
                            yield ParameterPermutation(cell_size=c, kernel=k, bw=bw, alpha=a)
                    else:
                        yield ParameterPermutation(cell_size=c, kernel=k, bw=bw, alpha=None)

    def __len__(self):
        return len(self.cell_sizes) * len(self.kernels) * len(self.bws) \
               * (1 + len(self.alphas) * len(self.alphas.intersection(NEEDS_ALPHA)))

    def __add__(self, other):
        if not other.instanceof(Parameters):
            raise SpatSegTypeError("{other} is not a {this}-class object!".format(other=other.__name__, this=self.__name__))

        self.cell_sizes.update(other.cell_sizes)
        self.kernels.update(other.kernels)
        self.bws.update(other.bws)
        self.alphas.update(other.alphas)

    def __sub__(self, other):
        if not other.instanceof(Parameters):
            raise SpatSegTypeError("{other} is not a {this}-class object!".format(other=other.__name__, this=self.__name__))

        self.cell_sizes.difference_update(other.cell_sizes)
        self.kernels.difference_update(other.kernels)
        self.bws.difference_update(other.bws)
        self.alphas.difference_update(other.alphas)
