from dataclasses import asdict
from typing import Optional

from ..viewer_state import ViewerState
from .interpolation_constants import Interpolation
from .typing import InterpolationMap
from .utils import keys_to_list, nested_get, nested_set


def interpolate_viewer_state(
    initial_state: ViewerState,
    final_state: ViewerState,
    fraction: float,
    interpolation_map: Optional[InterpolationMap] = None,
) -> ViewerState:
    """Interpolate a state between two states

    Parameters
    ----------
    initial_state : ViewerState
        Description of initial viewer state.
    final_state : ViewerState
        Description of final viewer state.
    fraction : float
        Interpolation fraction, must be between `0` and `1`.
        A value of `0` will return the initial state. A
        value of `1` will return the final state.
    interpolation_map : InterpolationMap or None
        Dictionary mapping state attribute keys to interpolation functions.

    Returns
    -------
    state : dict
        Description of viewer state.
    """

    viewer_state_data = {}

    initial_state = asdict(initial_state)
    final_state = asdict(final_state)

    for keys in keys_to_list(initial_state):
        v0 = nested_get(initial_state, keys)
        v1 = nested_get(final_state, keys)

        all_keys_are_strings = all([isinstance(key, str) for key in keys])
        if interpolation_map is not None and all_keys_are_strings:
            attribute_name = ".".join(keys)
            interpolation_function = interpolation_map.get(
                attribute_name, Interpolation.DEFAULT
            )
        else:
            interpolation_function = Interpolation.DEFAULT
        interpolated_value = interpolation_function(v0, v1, fraction)

        nested_set(viewer_state_data, keys, interpolated_value)

    return ViewerState(**viewer_state_data)
