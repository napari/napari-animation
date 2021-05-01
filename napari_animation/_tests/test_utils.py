import pytest

from ..utils import interpolate_state, keys_to_list, nested_get


@pytest.mark.parametrize("fraction", [0, 0.2, 0.4, 0.6, 0.8, 1])
def test_interpolate_state(key_frames, fraction):
    """Check that state interpolation works"""
    initial_state = key_frames[0]["viewer"]
    final_state = key_frames[1]["viewer"]
    result = interpolate_state(initial_state, final_state, fraction)
    assert len(result) == len(initial_state)
    if fraction == 0:
        assert result == initial_state
    elif fraction == 1:
        assert result == final_state
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
