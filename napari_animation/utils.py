from copy import deepcopy

import numpy as np


def interpolate_state(initial_state, final_state, fraction):
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

    Returns
    -------
    state : dict
        Description of viewer state.
    """
    # Once dataclasses in napari are typed we shouldn't need to test both the
    # initial and final states. Right now we need to test both for cases
    # where one can be None.
    if isinstance(initial_state, dict) and isinstance(final_state, dict):
        state = dict()
        for k in initial_state.keys():
            v0 = initial_state[k]
            v1 = final_state[k]
            state[k] = interpolate_state(v0, v1, fraction)
        return state

    elif isinstance(initial_state, float) and isinstance(final_state, float):
        return _interpolate_float(initial_state, final_state, fraction)

    elif isinstance(initial_state, int) and isinstance(final_state, int):
        return _interpolate_int(initial_state, final_state, fraction)

    elif isinstance(initial_state, (list, tuple)) and isinstance(final_state, (list, tuple)):
        return tuple(interpolate_state(v0, v1, fraction) for v0, v1 in zip(initial_state, final_state))

    else:  
        return _interpolate_bool(initial_state, final_state, fraction)


def _interpolate_float(a, b, fraction):
    return a + (b - a) * fraction


def _interpolate_int(a, b, fraction):
    return int(_interpolate_float(a, b, fraction))


def _interpolate_bool(a, b, fraction):
    if fraction < 0.5:
        return a
    else:
        return b
