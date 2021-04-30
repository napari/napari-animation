from enum import Enum
from functools import partial
import numpy as np
from napari._vispy.quaternion import quaternion2euler
from scipy.spatial.transform import Rotation as R
from scipy.spatial.transform import Slerp
from vispy.util.quaternion import Quaternion
import numbers


def default(a, b, fraction):
    """ Default to linear interpolation for the corresponding type."""
    if isinstance(a, numbers.Number) and isinstance(b, numbers.Number):
        return interpolate_num(a, b, fraction)

    elif isinstance(a, (list, tuple)) and isinstance(
        b, (list, tuple)
    ):
        return interpolate_seq(a, b, fraction)

    else:
        return interpolate_bool(a, b, fraction)


def interpolate_seq(a, b, fraction):
    """ Linear interpolation of list or tuple."""
    return type(a)(default(v0, v1, fraction) for v0, v1 in zip(a, b))


def interpolate_num(a, b, fraction):
    """ Linear interpolation for numeric types."""
    return type(a)(a + (b - a) * fraction)


def interpolate_bool(a, b, fraction):
    """ Step interpolation."""
    if fraction < 0.5:
        return a
    else:
        return b


def interpolate_log(a, b, fraction):
    """ Log interpolation, for camera zoom mostly."""
    c = interpolate_num(np.log10(a), np.log10(b), fraction)
    return np.power(10, c)


def slerp(a, b, fraction):
    """ Compute slerp from Euler angles, compatible with the napari view."""
    q1 = Quat2quat(Quaternion.create_from_euler_angles(*a, degrees=True))
    q2 = Quat2quat(Quaternion.create_from_euler_angles(*b, degrees=True))
    key_rots = R.from_quat([q1, q2])

    slerp = Slerp([0, 1], key_rots)
    q = quat2Quat(slerp(fraction).as_quat())
    return quaternion2euler(q, degrees=True)


def quat2Quat(quat):
    """ Convert scipy compatible quaternion to vispy Quaternion."""
    return Quaternion(quat[3], quat[0], quat[1], quat[2])


def Quat2quat(Quat):
    """ Convert vispy Quaternion to a scipy compatible quaternion."""
    return [Quat.x, Quat.y, Quat.z, Quat.w]


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