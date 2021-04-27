import numpy as np
from napari._vispy.quaternion import quaternion2euler
from scipy.spatial.transform import Rotation as R
from scipy.spatial.transform import Slerp
from vispy.util.quaternion import Quaternion

from .easing import Easing


def interpolate_state(initial_state, final_state, fraction, method={}):
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
    method : dict
        User supplied interpolation functions for
        corresponding keys in state dict.

    Returns
    -------
    state : dict
        Description of viewer state.
    """
    # Once dataclasses in napari are typed we shouldn't need to test both the
    # initial and final states. Right now we need to test both for cases
    # where one can be None.

    if hasattr(method, "__call__"):
        # If user provided some interpolation function
        return method(initial_state, final_state, fraction)

    else:
        if isinstance(initial_state, dict) and isinstance(final_state, dict):
            state = dict()
            for k in initial_state.keys():
                v0 = initial_state[k]
                v1 = final_state[k]
                m = method[k] if k in method else {}

                state[k] = interpolate_state(v0, v1, fraction, m)

            return state
        else:

            # Default mode
            if isinstance(initial_state, float) and isinstance(final_state, float):
                return _interpolate_float(initial_state, final_state, fraction)

            elif isinstance(initial_state, int) and isinstance(final_state, int):
                return _interpolate_int(initial_state, final_state, fraction)

            elif isinstance(initial_state, (list, tuple)) and isinstance(
                final_state, (list, tuple)
            ):
                return _interpolate_seq(initial_state, final_state, fraction)

            else:
                return _interpolate_bool(initial_state, final_state, fraction)


def _interpolate_seq(a, b, fraction):
    return type(a)(interpolate_state(v0, v1, fraction) for v0, v1 in zip(a, b))


def _interpolate_float(a, b, fraction):
    return float(a + (b - a) * fraction)


def _interpolate_int(a, b, fraction):
    return int(_interpolate_float(a, b, fraction))


def _interpolate_bool(a, b, fraction):
    if fraction < 0.5:
        return a
    else:
        return b


def _interpolate_zoom(a, b, fraction):
    c = _interpolate_float(np.log10(a), np.log10(b), fraction)
    return np.power(10, c)


def _interpolate_angles(a, b, fraction):
    q1 = Quat2quat(Quaternion.create_from_euler_angles(*a, degrees=True))
    q2 = Quat2quat(Quaternion.create_from_euler_angles(*b, degrees=True))
    key_rots = R.from_quat([q1, q2])

    slerp = Slerp([0, 1], key_rots)
    q = quat2Quat(slerp(fraction).as_quat())
    return quaternion2euler(q, degrees=True)


def quat2Quat(quat):
    return Quaternion(quat[3], quat[0], quat[1], quat[2])


def Quat2quat(Quat):
    return [Quat.x, Quat.y, Quat.z, Quat.w]


def _easing_func_to_name(easing_function):
    [name] = [e.name for e in Easing if e.value is easing_function]
    return name
