from enum import Enum, member
from functools import partial

from .base_interpolation import default_interpolation as _default_interpolation
from .base_interpolation import interpolate_bool as _interpolate_bool
from .base_interpolation import interpolate_log as _interpolate_log
from .base_interpolation import slerp as _slerp


class Interpolation(Enum):
    """Interpolation: interpolation function to use for a transition.

    Selects a preset interpolation function
        * DEFAULT: linear interpolation between start and endpoint.
        * SLERP: spherical linear interpolation on Euler angles.
        * LOG: log interpolation between start and endpoint.
        * BOOL: boolean interpolation between start and endpoint.

    """

    DEFAULT = member(partial(_default_interpolation))
    LOG = member(partial(_interpolate_log))
    SLERP = member(partial(_slerp))
    BOOL = member(partial(_interpolate_bool))

    def __call__(self, *args):
        return self.value(*args)
