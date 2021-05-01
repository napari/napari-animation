from .easing import Easing
from .interpolation import Interpolation, interpolation_dict


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

    state = dict()
    separator = "."

    for keys in keys_to_list(initial_state):
        v0 = nested_get(initial_state, keys)
        v1 = nested_get(final_state, keys)

        property_string = separator.join(keys)

        if property_string in interpolation_dict.keys():
            interpolation_func = interpolation_dict[property_string]
        else:
            interpolation_func = Interpolation.DEFAULT

        nested_set(state, keys, interpolation_func(v0, v1, fraction))

    return state


def _easing_func_to_name(easing_function):
    [name] = [e.name for e in Easing if e.value is easing_function]
    return name


def nested_get(input_dict, keys):
    """Get method for nested dictionaries.
    from https://codereview.stackexchange.com/a/156189
    """
    internal_dict_value = input_dict
    for k in keys:
        internal_dict_value = internal_dict_value.get(k, None)
        if internal_dict_value is None:
            return None
    return internal_dict_value


def nested_set(input_dict, keys, value):
    """ Set method for nested dictionaries."""
    dic = input_dict
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value


def keys_to_list(input_dict):
    for key, value in input_dict.items():
        if isinstance(value, dict) and value:
            for sub_key in keys_to_list(value):
                yield [key] + sub_key
        else:
            yield [key]
