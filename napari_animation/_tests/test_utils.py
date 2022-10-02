import pytest

from ..interpolation.utils import keys_to_list, nested_get

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
