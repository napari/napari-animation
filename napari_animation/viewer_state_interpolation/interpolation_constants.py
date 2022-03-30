from enum import Enum
from functools import partial

from .base_interpolation import default_interpolation as _default_interpolation
from .base_interpolation import interpolate_log as _interpolate_log
from .base_interpolation import slerp as _slerp


class Interpolation(Enum):
    """Interpolation: interpolation function to use for a transition.

    Selects a preset interpolation function
        * DEFAULT: linear interpolation between start and endpoint.
        * SLERP: spherical linear interpolation on Euler angles.
        * LOG: log interpolation between start and endpoint.

    """

    DEFAULT = partial(_default_interpolation)
    LOG = partial(_interpolate_log)
    SLERP = partial(_slerp)

    def __call__(self, *args):
        return self.value(*args)
