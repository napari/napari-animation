import numpy as np
from scipy.spatial.transform import Rotation

from .easing import Easing


def _easing_func_to_name(easing_function):
    """Get the name of an easing function."""
    [name] = [e.name for e in Easing if e is easing_function]
    return name


def nested_get(input_dict, keys_list):
    """Get method for nested dictionaries.

    Parameters
    ----------
    input_dict : dict
        Nested dictionary we want to get a value from.
    keys_list : list
        List of of keys pointing to the value to extract.

    Returns
    ----------
    internal_dict_value :
        The value that keys in keys_list are pointing to.
    """
    internal_dict_value = input_dict
    for k in keys_list:
        internal_dict_value = internal_dict_value.get(k, None)
        if internal_dict_value is None:
            return None
    return internal_dict_value


def nested_set(input_dict, keys_list, value):
    """Set method for nested dictionaries.

    Parameters
    ----------
    input_dict : dict
        Nested dictionary we want to get a value from.
    keys_list : list
        List of of keys pointing to the value to extract.
    value :
        Value to set at the required place.
    """
    dic = input_dict
    for key in keys_list[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys_list[-1]] = value


def keys_to_list(input_dict):
    """Yield the list of keys for each value deep in a nested dictionary.

    Parameters
    ----------
    input_dict : dict
        Nested dictionary we want to get of keys paths from.

    Returns
    ----------
    keys : list
        List of keys pointing to a deep value of the dictionary.
    """
    for key, value in input_dict.items():
        if isinstance(value, dict) and value:
            for sub_key in keys_to_list(value):
                yield [key] + sub_key
        else:
            yield [key]


def quaternion2euler(quaternion, degrees=False):
    """Converts scipy quaternion into euler angle representation.

    Euler angles have degeneracies, so the output might different
    from the Euler angles that might have been used to generate
    the input quaternion.

    Euler angles representation also has a singularity
    near pitch = Pi/2 ; to avoid this, we set to Pi/2 pitch angles
     that are closer than the chosen epsilon from it.

    Parameters
    ----------
    quaternion : list
        Quaternion for conversion in order [qx, qy, qz, qw].
    degrees : bool
        If output is returned in degrees or radians.

    Returns
    -------
    angles : 3-tuple
        Euler angles in (rx, ry, rz) order.
    """
    epsilon = 1e-10

    q = quaternion

    sin_theta_2 = 2 * (q[3] * q[1] - q[2] * q[0])
    sin_theta_2 = np.sign(sin_theta_2) * min(abs(sin_theta_2), 1)

    if abs(sin_theta_2) > 1 - epsilon:
        theta_1 = -np.sign(sin_theta_2) * 2 * np.arctan2(q[0], q[3])
        theta_2 = np.arcsin(sin_theta_2)
        theta_3 = 0

    else:
        theta_1 = np.arctan2(
            2 * (q[3] * q[2] + q[1] * q[0]),
            1 - 2 * (q[1] * q[1] + q[2] * q[2]),
        )

        theta_2 = np.arcsin(sin_theta_2)

        theta_3 = np.arctan2(
            2 * (q[3] * q[0] + q[1] * q[2]),
            1 - 2 * (q[0] * q[0] + q[1] * q[1]),
        )

    angles = (theta_1, theta_2, theta_3)

    if degrees:
        return tuple(np.degrees(angles))
    else:
        return angles


class ExtraSlerp:
    """Spherical Linear Interpolation and Extrapolation of Rotations.

    Taken from scipy.spatial.transform.slerp and modified for extrapolation.

    The interpolation between consecutive rotations is performed as a rotation
    around a fixed axis with a constant angular velocity [1]_. This ensures
    that the interpolated rotations follow the shortest path between initial
    and final orientations.
    Parameters
    ----------
    times : array_like, shape (N,)
        Times of the known rotations. At least 2 times must be specified.
    rotations : `Rotation` instance
        Rotations to perform the interpolation between. Must contain N
        rotations.
    Methods
    -------
    __call__

    """

    def __init__(self, times, rotations):
        if rotations.single:
            raise ValueError("`rotations` must be a sequence of rotations.")

        if len(rotations) == 1:
            raise ValueError(
                "`rotations` must contain at least 2 " "rotations."
            )

        times = np.asarray(times)
        if times.ndim != 1:
            raise ValueError(
                "Expected times to be specified in a 1 "
                "dimensional array, got {} "
                "dimensions.".format(times.ndim)
            )

        if times.shape[0] != len(rotations):
            raise ValueError(
                "Expected number of rotations to be equal to "
                "number of timestamps given, got {} rotations "
                "and {} timestamps.".format(len(rotations), times.shape[0])
            )
        self.times = times
        self.timedelta = np.diff(times)

        if np.any(self.timedelta <= 0):
            raise ValueError("Times must be in strictly increasing order.")

        self.rotations = rotations[:-1]
        self.rotvecs = (self.rotations.inv() * rotations[1:]).as_rotvec()

    def __call__(self, times):
        """Interpolate rotations.
        Compute the interpolated rotations at the given `times`.
        Parameters
        ----------
        times : array_like
            Times to compute the interpolations at. Can be a scalar or
            1-dimensional.
        Returns
        -------
        interpolated_rotation : `Rotation` instance
            Object containing the rotations computed at given `times`.
        """
        # Clearly differentiate from self.times property
        compute_times = np.asarray(times)
        if compute_times.ndim > 1:
            raise ValueError("`times` must be at most 1-dimensional.")

        single_time = compute_times.ndim == 0
        compute_times = np.atleast_1d(compute_times)

        # side = 'left' (default) excludes t_min.
        ind = np.searchsorted(self.times, compute_times) - 1
        # Include t_min. Without this step, index for t_min equals -1
        ind[compute_times == self.times[0]] = 0
        # if np.any(np.logical_or(ind < 0, ind > len(self.rotations) - 1)):
        #     raise ValueError("Interpolation times must be within the range "
        #                      "[{}, {}], both inclusive.".format(
        #                         self.times[0], self.times[-1]))

        alpha = (compute_times - self.times[ind]) / self.timedelta[ind]

        result = self.rotations[ind] * Rotation.from_rotvec(
            self.rotvecs[ind] * alpha[:, None]
        )

        if single_time:
            result = result[0]

        return result
