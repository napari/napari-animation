from numbers import Number
from typing import Sequence, Tuple, TypeVar

import numpy as np
from scipy.spatial.transform import Rotation as R

_T = TypeVar("_T")


def default_interpolation(a: _T, b: _T, fraction: float) -> _T:
    """Default interpolation for the corresponding type;
    linear interpolation for numeric, instantaneous transition otherwise.

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
    if isinstance(a, bool) or isinstance(b, bool):
        # checking this first because booleans are numbers
        return interpolate_bool(a, b, fraction)

    elif isinstance(a, Number) and isinstance(b, Number):
        return interpolate_num(a, b, fraction)

    elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return interpolate_sequence(a, b, fraction)

    else:
        # strings, etc.
        return interpolate_bool(a, b, fraction)


def interpolate_sequence(
    a: Sequence[_T], b: Sequence[_T], fraction: float
) -> Sequence[_T]:
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
    seq_cls = type(a)
    return seq_cls(
        default_interpolation(v0, v1, fraction) for v0, v1 in zip(a, b)
    )


def interpolate_num(a: Number, b: Number, fraction: float) -> Number:
    """Linear interpolation for numeric types.

    Parameters
    ----------
    a : Number
        initial value
    b : Number
        final value
    fraction : float
        fraction to interpolate to between a and b.

    Returns
    ----------
        : numeric type
    Interpolated value between a and b at fraction.
    """
    number_cls = type(a)
    return number_cls(a + (b - a) * fraction)


def interpolate_bool(a: bool, b: bool, fraction: float) -> bool:
    """Instantaneous transition from a to b.

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
        b if any step was taken into its direction, otherwise a.
    """
    if fraction > 0.0:
        return b
    else:
        return a


def interpolate_log(a: float, b: float, fraction: float) -> float:
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


def slerp(
    a: Tuple[float, float, float],
    b: Tuple[float, float, float],
    fraction: float,
) -> Tuple[float, float, float]:
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
