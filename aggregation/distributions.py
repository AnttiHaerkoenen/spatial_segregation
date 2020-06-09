from abc import ABC, abstractmethod

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import betabinom, gamma


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
        plt.vlines(
            x,
            0,
            betabinom(**self.parameters).pmf(x),
            label='pmf',
            **kwargs,
        )


class Gamma(Distribution):
    name = 'Gamma'

    def __init__(
            self,
            shape: float,
            scale: float,
    ):
        self.a = shape
        self.scale = scale

    def __str__(self):
        return f'{self.name} Distribution (shape={self.a}, scale={self.scale})'

    @property
    def parameters(self):
        return {
            'a': self.a,
            'scale': self.scale,
        }

    def draw(self, size):
        series = pd.Series(
            gamma.rvs(**self.parameters, size=size))
        return series

    def plot(self, **kwargs):
        x = np.linspace(
            gamma.ppf(0.01, **self.parameters),
            gamma.ppf(0.99, **self.parameters),
            100,
        )
        plt.plot(
            x,
            gamma.pdf(x, **self.parameters),
            label='pdf',
            **kwargs
        )


if __name__ == '__main__':
    beta_binom = BetaBinomial(28, 1, 2)
    beta_binom.plot()
    plt.show()

    # g = Gamma(1.25, 5)
    # g.plot()
    # plt.show()
