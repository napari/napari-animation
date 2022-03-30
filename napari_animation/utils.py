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
    return zip(a, b)
