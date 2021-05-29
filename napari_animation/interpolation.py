import numbers
from enum import Enum
from functools import partial
from typing import Dict

import numpy as np
from scipy.spatial.transform import Rotation as R


def default(a, b, fraction):
    """Default interpolation for the corresponding type;
    linear interpolation for numeric, step interpolation otherwise.

    Parameters
    ----------
    a :
        initial value
    b :
        final value
    fraction : float
        fraction to interpolate to between a and b.

    Returns
    ----------
        Interpolated value between a and b at fraction.
    """
    if isinstance(a, numbers.Number) and isinstance(b, numbers.Number):
        return interpolate_num(a, b, fraction)

    elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return interpolate_seq(a, b, fraction)

    else:
        return interpolate_bool(a, b, fraction)


def interpolate_seq(a, b, fraction):
    """Interpolation of list or tuple.
    Parameters
    ----------
    a : list or tuple
        initial sequence
    b : list or tuple
        final sequence
    fraction : float
        fraction to interpolate to between a and b.

    Returns
    ----------
        : sequence of type a
    Interpolated sequence between a and b at fraction.
    """
    return type(a)(default(v0, v1, fraction) for v0, v1 in zip(a, b))


def interpolate_num(a, b, fraction):
    """Linear interpolation for numeric types.

    Parameters
    ----------
    a : numeric type
        initial value
    b : numeric type
        final value
    fraction : float
        fraction to interpolate to between a and b.

    Returns
    ----------
        : numeric type
    Interpolated value between a and b at fraction.
    """
    return type(a)(a + (b - a) * fraction)


def interpolate_bool(a, b, fraction):
    """Step interpolation.

    Parameters
    ----------
    a :
        initial value
    b :
        final value
    fraction : float
        fraction to interpolate to between a and b.

    Returns
    ----------
    a or b :
        Step interpolated value between a and b.
    """
    if fraction < 0.5:
        return a
    else:
        return b


def interpolate_log(a, b, fraction):
    """Log interpolation, for camera zoom mostly.

    Parameters
    ----------
    a : float
        initial value
    b : float
        final value
    fraction : float
        fraction to interpolate to between a and b.

    Returns
    ----------
        : float
    Log interpolated value between a and b at fraction.
    """
    c = interpolate_num(np.log10(a), np.log10(b), fraction)
    return np.power(10, c)


def slerp(a, b, fraction):
    """Compute Spherical linear interpolation from Euler angles,
    compatible with the napari view.

    Parameters
    ----------
    a : tuple
        initial tuple of Euler angles in degrees.
    b : tuple
        final tuple of Euler angles in degrees.
    fraction : float
        fraction to interpolate to between a and b.

    Returns
    ----------
        : tuple
    Interpolated Euler angles between a and b at fraction.
    """
    initial_rotation, final_rotation = R.from_euler(
        "ZYX", [a, b], degrees=True
    )
    rotation_vector = (initial_rotation.inv() * final_rotation).as_rotvec()
    rotation_vector *= fraction
    c_rotation = initial_rotation * R.from_rotvec(rotation_vector)
    return c_rotation.as_euler("ZYX", degrees=True)


class Interpolation(Enum):
    """Interpolation: interpolation function to use for a transition.

    Selects a preset interpolation function
        * DEFAULT: linear interpolation between start and endpoint.
        * SLERP: spherical linear interpolation on Euler angles.
        * LOG: log interpolation between start and endpoint.

    """

    DEFAULT = partial(default)
    LOG = partial(interpolate_log)
    SLERP = partial(slerp)

    def __call__(self, *args):
        return self.value(*args)


InterpolationMap = Dict[str, Interpolation]
