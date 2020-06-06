from abc import ABC, abstractmethod

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import betabinom


class Distribution(ABC):
    @abstractmethod
    def draw(self, size: int) -> pd.Series:
        pass

    @abstractmethod
    def plot(self, **kwargs):
        pass

    @property
    @abstractmethod
    def parameters(self):
        pass


class BetaBinomial(Distribution):
    name = 'Beta-Binomial'

    def __init__(
            self,
            n: int,
            a: float,
            b: float,
    ):
        self.n = n
        self.a = a
        self.b = b

    def __str__(self):
        return f'{self.name} Distribution (n={self.n}, a={self.a}, b={self.b})'

    @property
    def parameters(self):
        return {
            'n': self.n,
            'a': self.a,
            'b': self.b,
        }

    def draw(self, size):
        series = pd.Series(
            betabinom.rvs(**self.parameters, size=size))

        return series

    def plot(self, **kwargs):
        x = np.arange(
            betabinom.ppf(0.01, **self.parameters),
            betabinom.ppf(0.99, **self.parameters),
        )
        plt.vlines(x, 0, betabinom(**self.parameters).pmf(x), **kwargs)


if __name__ == '__main__':
    beta_binom = BetaBinomial(28, 1, 2)
    beta_binom.plot()
    plt.show()
