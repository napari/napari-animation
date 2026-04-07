import numpy as np
import pytest
from napari.utils.colormaps import DirectLabelColormap

from ..interpolation.utils import keys_to_list, nested_get
from ..utils import layer_attribute_changed

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


def test_layer_attribute_changed_direct_label_colormap_equal():
    cmap1 = DirectLabelColormap(
        color_dict={None: 'black', 1: 'red', 2: 'blue'}
    )
    cmap2 = DirectLabelColormap(
        color_dict={None: 'black', 1: 'red', 2: 'blue'}
    )

    assert not layer_attribute_changed(cmap1, cmap2)


def test_layer_attribute_changed_direct_label_colormap_changed():
    cmap1 = DirectLabelColormap(
        color_dict={None: 'black', 1: 'red', 2: 'blue'}
    )
    cmap2 = DirectLabelColormap(
        color_dict={None: 'black', 1: 'red', 2: 'green'}
    )

    assert layer_attribute_changed(cmap1, cmap2)


def test_layer_attribute_changed_tuple_equal():
    """Tuples (like _label_mapping_and_color_dict) should be compared element-by-element."""
    arr = np.array([1.0, 0.0, 0.0, 1.0])
    t1 = ({None: 0, 1: 1}, {0: arr, 1: arr})
    t2 = ({None: 0, 1: 1}, {0: arr, 1: arr})

    assert not layer_attribute_changed(t1, t2)


def test_layer_attribute_changed_tuple_changed():
    arr1 = np.array([1.0, 0.0, 0.0, 1.0])
    arr2 = np.array([0.0, 1.0, 0.0, 1.0])
    t1 = ({None: 0, 1: 1}, {0: arr1, 1: arr1})
    t2 = ({None: 0, 1: 1}, {0: arr2, 1: arr2})

    assert layer_attribute_changed(t1, t2)


class DictOnlyModel:
    def __init__(self, data):
        self._data = data

    def dict(self):
        return self._data


def test_layer_attribute_changed_dict_model_equal():
    model1 = DictOnlyModel({'color_dict': {1: np.array([1, 0, 0, 1])}})
    model2 = DictOnlyModel({'color_dict': {1: np.array([1, 0, 0, 1])}})

    assert not layer_attribute_changed(model1, model2)


def test_layer_attribute_changed_dict_model_changed():
    model1 = DictOnlyModel({'color_dict': {1: np.array([1, 0, 0, 1])}})
    model2 = DictOnlyModel({'color_dict': {1: np.array([0, 1, 0, 1])}})

    assert layer_attribute_changed(model1, model2)
