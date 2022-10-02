from dataclasses import asdict

import numpy as np
import pytest

from napari_animation.interpolation import interpolate_viewer_state
from napari_animation.interpolation.base_interpolation import (
    interpolate_bool,
    interpolate_log,
    interpolate_num,
    interpolate_sequence,
)
from napari_animation.interpolation.utils import nested_assert_close


# Actual tests
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
    result = interpolate_sequence(a, b, fraction)
    assert isinstance(result, type(a))
    assert result == expected


@pytest.mark.parametrize("a", [True, False])
@pytest.mark.parametrize("b", [True, False])
@pytest.mark.parametrize("fraction", [0, 0.25, 0.75, 1])
def test_interpolate_bool(a, b, fraction):
    result = interpolate_bool(a, b, fraction)
    if fraction > 0.0:
        assert result == b
    else:
        assert result == a


@pytest.mark.parametrize("a", [1.0, 1])
@pytest.mark.parametrize("b", [10.0, 10])
@pytest.mark.parametrize("fraction", [0, 0.0, 0.5, 1.0, 1])
def test_interpolate_log(a, b, fraction):
    """Check that log interpolation produces valid output"""
    result = interpolate_log(a, b, fraction)
    assert result == np.power(10, fraction)


@pytest.mark.parametrize("fraction", [0, 0.2, 0.4, 0.6, 0.8, 1])
def test_interpolate_viewer_state(frame_sequence, fraction):
    """Check that state interpolation works"""
    initial_state = frame_sequence[0]
    final_state = frame_sequence[-1]
    result = interpolate_viewer_state(initial_state, final_state, fraction)
    assert len(asdict(result)) == len(asdict(initial_state))
    if fraction == 0:
        # assert result == initial_state
        nested_assert_close(asdict(result), asdict(initial_state))
    elif fraction == 1:
        # assert result == final_state
        nested_assert_close(asdict(result), asdict(final_state))

    # else:
    # should find something else to test
