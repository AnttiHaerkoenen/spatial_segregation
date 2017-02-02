import math

from hypothesis import given
import hypothesis.strategies as st

import src.kernel_functions as kf


@given(bw=st.floats(0.1, 100000),
       a=st.floats(0, 1000),
       c=st.floats(0, 100000))
def test_distance_decay(bw, a, c):
    assert kf.distance_decay(d=bw, bw=bw, a=a) == 0, "d = bw"
    assert kf.distance_decay(d=bw + c, bw=bw, a=a) == 0, "d > bw"
    assert abs(kf.distance_decay(0, bw, a) - 1) < 0.0001, "d = 0"
    assert abs(kf.distance_decay(d=bw/2, bw=bw, a=a) - 0.6 ** a) < 0.0001, "d = bw/2"


@given(bw=st.floats(0.1, 10000),
       c1=st.floats(0, 10000),
       c2=st.floats(0.1, 1000))
def test_gauss(bw, c1, c2):
    assert kf.gaussian(0, bw) == 1 / (math.sqrt(2 * math.pi) * bw ** 2), "d = 0"
    assert kf.gaussian(c1, bw) >= kf.gaussian(c1 + c2, bw)


if __name__ == '__main__':
    test_distance_decay()
    test_gauss()
    # test_uniform()
    # test_epanechnikov()
    # test_triangle()
