import numpy as np
import pytest
from scipy.spatial.transform import Rotation as R

from ..easing import Easing
from ..utils import (
    _easing_func_to_name,
    keys_to_list,
    nested_get,
    quaternion2euler,
)

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


# Euler angles to be tested, in degrees
angles = [[12, 53, 92], [180, -90, 0], [16, 90, 0]]

# Prepare for input and add corresponding values in radians
angles_param = [(x, True) for x in angles]
angles_param.extend([(x, False) for x in np.radians(angles)])


@pytest.mark.parametrize("angles,degrees", angles_param)
def test_quaternion2euler(angles, degrees):
    """Test quaternion to euler angle conversion."""

    # Test for degrees
    q = R.from_euler("ZYX", angles, degrees).as_quat()
    ea = quaternion2euler(q, degrees=degrees)

    np.testing.assert_allclose(ea, angles)


@pytest.mark.parametrize(
    "easing_function,expected",
    [(Easing.LINEAR, "LINEAR"), (Easing.CIRCULAR, "CIRCULAR")],
)
def test_easing_func_to_name(easing_function, expected):
    result = _easing_func_to_name(easing_function)
    assert result == expected
