import numbers

import numpy as np
import pytest

from ..utils import interpolate_state, keys_to_list, nested_get


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


input_dict = [{"a": 1, "b": {"c": "d"}}]
keys = [["b", "c"]]
expected = ["d"]
test_set = [param for param in zip(input_dict, keys, expected)]


@pytest.mark.parametrize("input_dict,keys,expected", test_set)
def test_nested_get(input_dict, keys, expected):
    result = nested_get(input_dict, keys)
    assert result == expected


input_dict = [{"a": 1, "b": {"c": "d"}, "e": {}}]
expected = [[["a"], ["b", "c"], ["e"]]]
test_set = [param for param in zip(input_dict, expected)]


@pytest.mark.parametrize("input_dict,expected", test_set)
def test_keys_to_list(input_dict, expected):
    result = [keys for keys in keys_to_list(input_dict)]
    for keys in result:
        assert isinstance(keys, list)
    assert result == expected
