import numpy as np
import pytest
from vispy.util.quaternion import Quaternion as Q

from napari_animation.interpolation import (
    Quat2quat,
    interpolate_bool,
    interpolate_log,
    interpolate_num,
    interpolate_seq,
    quat2Quat,
)


@pytest.mark.parametrize("a", [0.0, 0])
@pytest.mark.parametrize("b", [100.0, 100])
@pytest.mark.parametrize("fraction", [0, 0.0, 0.5, 1.0, 1])
def test_interpolate_num(a, b, fraction):
    """Check that interpolation of numbers produces valid output"""
    result = interpolate_num(a, b, fraction)
    assert isinstance(result, type(a))
    assert result == fraction * b


@pytest.mark.parametrize("a,b", [([0.0, 0.0, 0.0], [1.0, 1.0, 1.0])])
@pytest.mark.parametrize(
    "fraction,expected",
    [(0.0, [0.0, 0.0, 0.0]), (0.5, [0.5, 0.5, 0.5]), (1.0, [1.0, 1.0, 1.0])],
)
def test_interpolate_seq(a, b, fraction, expected):
    """Check that interpolation of sequences produces valid output"""
    result = interpolate_seq(a, b, fraction)
    assert isinstance(result, type(a))
    assert result == expected


@pytest.mark.parametrize("a", [True, False])
@pytest.mark.parametrize("b", [True, False])
@pytest.mark.parametrize("fraction", [0, 0.25, 0.75, 1])
def test_interpolate_bool(a, b, fraction):
    result = interpolate_bool(a, b, fraction)
    if fraction < 0.5:
        assert result == a
    else:
        assert result == b


@pytest.mark.parametrize("a", [1.0, 1])
@pytest.mark.parametrize("b", [10.0, 10])
@pytest.mark.parametrize("fraction", [0, 0.0, 0.5, 1.0, 1])
def test_interpolate_log(a, b, fraction):
    """Check that log interpolation produces valid output"""
    result = interpolate_log(a, b, fraction)
    assert result == np.power(10, fraction)


@pytest.mark.parametrize("quat,expected", [([1, 2, 3, 4], Q(4, 1, 2, 3))])
def test_quat2Quat(quat, expected):
    """Check that it converts scipy compatible quaternion to vispy Quaternion."""
    result = quat2Quat(quat)
    assert isinstance(result, Q)
    assert [result.x, result.y, result.z, result.w] == [
        expected.x,
        expected.y,
        expected.z,
        expected.w,
    ]


@pytest.mark.parametrize(
    "Quat,expected", [(Q(4, 1, 2, 3, normalize=False), [1, 2, 3, 4])]
)
def test_Quat2quat(Quat, expected):
    """Check that it converts vispy Quaternion to scipy compatible quaternion."""
    result = Quat2quat(Quat)
    assert isinstance(result, list)
    assert result == expected
