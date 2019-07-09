import os
from abc import abstractmethod, ABC

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def _quartic(_, r, bw):
    return np.where(r < bw, (1 - (r/bw) ** 2) ** 2, 0)


class Kernel(ABC):
    function = None
    name = None

    def __init__(self, bandwidth):
        self.bandwidth = bandwidth

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError


class QuarticKernel(Kernel):
    name = 'quartic kernel'
    function = _quartic

    def __init__(self, bandwidth):
        super().__init__(bandwidth=bandwidth)

    def __call__(self, r):
        return self.function(r=r, bw=self.bandwidth)

    def __eq__(self, other):
        return self.name == other.name and self.bandwidth == other.bandwidth

    def __str__(self):
        return f"Quartic kernel function (bandwidth={self.bandwidth})"


if __name__ == '__main__':
    pass
