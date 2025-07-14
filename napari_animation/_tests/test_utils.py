import pytest

from ..interpolation.utils import keys_to_list, nested_get

input_dict = [{"a": 1, "b": {"c": "d"}}]
keys = [["b", "c"]]
expected = ["d"]
test_set = list(zip(input_dict, keys, expected, strict=False))


@pytest.mark.parametrize("input_dict,keys,expected", test_set)
def test_nested_get(input_dict, keys, expected):
    result = nested_get(input_dict, keys)
    assert result == expected


input_dict = [{"a": 1, "b": {"c": "d"}, "e": {}}]
expected = [[["a"], ["b", "c"], ["e"]]]
test_set = list(zip(input_dict, expected, strict=False))


@pytest.mark.parametrize("input_dict,expected", test_set)
def test_keys_to_list(input_dict, expected):
    result = list(keys_to_list(input_dict))
    for keys in result:
        assert isinstance(keys, list)
    assert result == expected
