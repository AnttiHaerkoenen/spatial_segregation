from hypothesis import given
import hypothesis.strategies as st
from hypothesis.extra.numpy import arrays
import numpy as np

import spatial_segregation.segregation_indices as si


@given(arrays(dtype=np.float32, shape=(50, 2)))
def test_km_identical(data):
    assert si.km(data) - si.km(data) < 0.0001


@given(st.integers())
def test_km_total_segregation(data):
    pass


@given()
def test_km_no_segregation(data):
    pass
