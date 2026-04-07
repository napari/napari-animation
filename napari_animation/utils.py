import itertools

import numpy as np


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
    return zip(a, b, strict=False)


def layer_attribute_changed(value, original_value):
    """Recursively check if a layer attribute has changed."""
    # Handle EventedModel-like objects (napari 0.7.x has model_dump, 0.6.x has dict)
    value_dump = getattr(value, "model_dump", None)
    if callable(value_dump):
        return layer_attribute_changed(
            value_dump(), original_value.model_dump()
        )

    value_dict = getattr(value, "dict", None)
    if callable(value_dict):
        return layer_attribute_changed(value_dict(), original_value.dict())

    if isinstance(value, dict):
        if (
            not isinstance(original_value, dict)
            or value.keys() != original_value.keys()
        ):
            return True
        return any(
            layer_attribute_changed(value[key], original_value[key])
            for key in value
        )
    if isinstance(value, tuple):
        if not isinstance(original_value, tuple) or len(value) != len(
            original_value
        ):
            return True
        return any(
            layer_attribute_changed(v, ov)
            for v, ov in zip(value, original_value, strict=False)
        )
    return not np.array_equal(value, original_value)
