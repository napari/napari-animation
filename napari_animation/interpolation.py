import numbers
from enum import Enum
from functools import partial

import numpy as np
from scipy.spatial.transform import Rotation as R
from scipy.spatial.transform import Slerp

from .utils import keys_to_list, nested_get, nested_set, quaternion2euler


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
    key_rots = R.from_euler("ZYX", [a, b], degrees=True)
    slerped = Slerp([0, 1], key_rots)
    q = slerped(fraction).as_quat()
    return quaternion2euler(q, degrees=True)


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


def interpolate_state(
    initial_state, final_state, fraction, state_interpolation_map={}
):
    """Interpolate a state between two states

    Parameters
    ----------
    initial_state : dict
        Description of initial viewer state.
    final_state : dict
        Description of final viewer state.
    fraction : float
        Interpolation fraction, must be between `0` and `1`.
        A value of `0` will return the initial state. A
        value of `1` will return the final state.
    state_interpolation_map : dict
        Dictionary relating state attributes to interpolation functions.

    Returns
    -------
    state : dict
        Description of viewer state.
    """

    state = dict()
    separator = "."

    for keys in keys_to_list(initial_state):
        v0 = nested_get(initial_state, keys)
        v1 = nested_get(final_state, keys)

        property_string = separator.join(keys)

        if property_string in state_interpolation_map.keys():
            interpolation_func = state_interpolation_map[property_string]
        else:
            interpolation_func = Interpolation.DEFAULT

        nested_set(state, keys, interpolation_func(v0, v1, fraction))

    return state
