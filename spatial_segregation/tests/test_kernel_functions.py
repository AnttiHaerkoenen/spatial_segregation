from hypothesis import given
import hypothesis.strategies as st

import spatial_segregation.kernel_functions as kf


@given(bw=st.integers(0, 1000000),
       a=st.integers(0, 1000000),
       c=st.integers(0, 1000000))
def test_dd_zero(bw, a, c):
    assert kf.distance_decay(d=bw, bw=bw, a=a) == 0
    assert kf.distance_decay(d=bw + c, bw=bw, a=a) == 0


@given(bw=st.integers(0, 1000000),
       a=st.integers(0, 1000000))
def test_dd_center(bw, a):
    assert kf.distance_decay(0, bw, a) - 1 < 0.00001


@given(bw=st.integers(0, 1000000),
       a=st.integers(0, 1000000))
def test_dd_halfway(bw, a):
    assert kf.distance_decay(d=bw/2, bw=bw, a=a) - 0.6**a < 0.00001
