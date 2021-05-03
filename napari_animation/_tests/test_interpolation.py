import numbers

import numpy as np
import pytest

from napari_animation.interpolation import (
    interpolate_bool,
    interpolate_log,
    interpolate_num,
    interpolate_seq,
    interpolate_state,
)

from ..utils import keys_to_list, nested_get


# Define some functions used for testing
def nested_assert_close(a, b):
    """ Assert close on nested dicts."""
    a_keys = [key for key in keys_to_list(a)]
    b_keys = [key for key in keys_to_list(b)]

    assert a_keys == b_keys

    for key in a_keys:
        a_1 = nested_get(a, key)
        b_1 = nested_get(b, key)

        nested_seq_assert_close(a_1, b_1)


def nested_seq_assert_close(a, b):
    """ Assert close to scalar or potentially nested qequences of numeric types and others."""
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        assert type(a) == type(b)
        for a_v, b_v in zip(a, b):
            nested_seq_assert_close(a_v, b_v)
    else:
        if isinstance(a, numbers.Number):
            np.testing.assert_allclose(a, b)
        else:
            assert a == b


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


@pytest.mark.parametrize("fraction", [0, 0.2, 0.4, 0.6, 0.8, 1])
def test_interpolate_state(key_frames, fraction):
    """Check that state interpolation works"""
    initial_state = key_frames[0]["viewer"]
    final_state = key_frames[1]["viewer"]
    result = interpolate_state(initial_state, final_state, fraction)
    assert len(result) == len(initial_state)
    if fraction == 0:
        # assert result == initial_state
        nested_assert_close(result, initial_state)
    elif fraction == 1:
        # assert result == final_state
        nested_assert_close(result, final_state)

    # else:
    # should find something else to test
