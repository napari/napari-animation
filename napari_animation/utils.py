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
