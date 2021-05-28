import itertools
import numbers

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


def make_thumbnail(image: np.ndarray, shape=(30, 30, 4)) -> np.ndarray:
    """Resizes an image to `shape` with padding"""
    from napari.layers.utils.layer_utils import convert_to_uint8
    from scipy import ndimage as ndi

    scale_factor = np.min(np.divide(shape, image.shape))
    intermediate_image = ndi.zoom(image, (scale_factor, scale_factor, 1))

    padding_needed = np.subtract(shape, intermediate_image.shape)
    pad_amounts = [(p // 2, (p + 1) // 2) for p in padding_needed]
    thumbnail = np.pad(intermediate_image, pad_amounts, mode="constant")
    thumbnail = convert_to_uint8(thumbnail)

    # blend thumbnail with opaque black background
    background = np.zeros(shape, dtype=np.uint8)
    background[..., 3] = 255

    f_dest = thumbnail[..., 3][..., None] / 255
    f_source = 1 - f_dest
    thumbnail = thumbnail * f_dest + background * f_source
    return thumbnail.astype(np.uint8)


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


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
    """Assert close to scalar or potentially nested qequences of numeric types and others."""
    if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)):
        for a_v, b_v in zip(a, b):
            nested_seq_assert_close(a_v, b_v)
    else:
        if isinstance(a, numbers.Number):
            np.testing.assert_allclose(a, b)
        else:
            assert a == b
