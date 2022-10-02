from numbers import Number

import numpy as np


def nested_get(input_dict, keys_list):
    """Get method for nested dictionaries.

    Parameters
    ----------
    input_dict : dict
        Nested dictionary we want to get a value from.
    keys_list : list
        List of of keys pointing to the value to extract.

    Returns
    ----------
    internal_dict_value :
        The value that keys in keys_list are pointing to.
    """
    internal_dict_value = input_dict
    for k in keys_list:
        internal_dict_value = internal_dict_value.get(k, None)
        if internal_dict_value is None:
            return None
    return internal_dict_value


def nested_set(input_dict, keys_list, value):
    """Set method for nested dictionaries.

    Parameters
    ----------
    input_dict : dict
        Nested dictionary we want to get a value from.
    keys_list : list
        List of of keys pointing to the value to extract.
    value :
        Value to set at the required place.
    """
    dic = input_dict
    for key in keys_list[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys_list[-1]] = value


def keys_to_list(input_dict):
    """Yield the list of keys for each value deep in a nested dictionary.

    Parameters
    ----------
    input_dict : dict
        Nested dictionary we want to get of keys paths from.

    Returns
    ----------
    keys : list
        List of keys pointing to a deep value of the dictionary.
    """
    for key, value in input_dict.items():
        if isinstance(value, dict) and value:
            for sub_key in keys_to_list(value):
                yield [key] + sub_key
        else:
            yield [key]


def nested_assert_close(a, b):
    """Assert close on nested dicts."""
    a_keys = [key for key in keys_to_list(a)]
    b_keys = [key for key in keys_to_list(b)]

    assert a_keys == b_keys

    for key in a_keys:
        a_1 = nested_get(a, key)
        b_1 = nested_get(b, key)

        nested_seq_assert_close(a_1, b_1)


def nested_seq_assert_close(a, b):
    """Assert close to scalar or potentially nested qequences of numeric types and others."""
    if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)):
        for a_v, b_v in zip(a, b):
            nested_seq_assert_close(a_v, b_v)
    else:
        if isinstance(a, Number):
            np.testing.assert_allclose(a, b)
        else:
            assert a == b
