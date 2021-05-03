import numpy as np

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
