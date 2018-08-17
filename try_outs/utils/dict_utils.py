#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import numbers  # required to check for numeric types

from copy import deepcopy
from functools import reduce

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


SYMBOL_KEY_CHAINING = "|"


def _deep_dict_breadth_first(d: dict, key: str):

    cur_level = 0
    level_found = 100**100
    stack = [(cur_level, [], d)]

    final_path = None
    val = None

    while stack:

        cur_level, cur_path, iter_stack = stack[0]

        for k, v in iter_stack.items():
            if k == key and cur_level <= level_found:

                if val is not None:
                    raise ValueError

                val = v
                cur_path.append(k)
                level_found = cur_level
                final_path = deepcopy(cur_path)
            elif isinstance(v, dict):
                path = deepcopy(cur_path)
                path.append(k)
                stack.append((cur_level+1, path, v))
        else:
            stack = stack[1:]

    return val, final_path


def key_split(key: str):
    path = key.split("|")
    return path[:-1], path[-1]


def _handle_chained_keys(d, key, check_final_leaf, check_unique_key):
    key_chain = key.split(SYMBOL_KEY_CHAINING)      # get the user specified key chain
    cur_d = deepcopy(d)                             # start with the root dict
    cur_p = list()

    if len(key_chain) == 2 and key_chain[0] == "":  # special case if value follows root
        val, path = _deep_dict_breadth_first(d, key_chain[1])  # look directly breath first for the target value
        return val, path
    else:

        if key_chain[0] == "":                              # remove unnecessary root and remove empty
            key_chain = key_chain[1:]

        for k in key_chain[:-1]:                            # do breath first for all path-descriptive keys
            d_, p_ = _deep_dict_breadth_first(cur_d, k)
            cur_d = deepcopy(d_)
            cur_p += p_

        val, p_ = deep_dict_lookup(cur_d, key_chain[-1],    # carry out depth first for last sub-dictionary
                                   check_final_leaf=check_final_leaf,
                                   check_unique_key=check_unique_key)

    cur_p += p_
    return val, cur_p


def deep_dict_lookup(d: dict, key: str, check_final_leaf=True, check_unique_key=True):
    """Return a value corresponding to the specified key in the (possibly nested) dictionary d. If there is no item
    with that key raise ValueError.

    :param d: dictionary to look up the key
    :param key: key to look up deep in `d`
    :param check_final_leaf: checks if the returned value is a final value and not another sub-directory
    :param check_unique_key: checks if there are multiple keys with name `key`; if yes throw ValueError
    """
    # "Stack of Iterators" pattern: http://garethrees.org/2016/09/28/pattern/
    # https://stackoverflow.com/questions/14962485/finding-a-key-recursively-in-a-dictionary

    if SYMBOL_KEY_CHAINING in key:
        return _handle_chained_keys(d, key, check_final_leaf=check_final_leaf, check_unique_key=check_unique_key)

    value = None

    current_path = []         # store the absolute path to the variable as a list of keys
    path_to_value = None      # path to the final key

    stack = [iter(d.items())]
    while stack:
        for k, v in stack[-1]:               # go through (sub-) directories
            current_path.append(k)
            if k == key:                     # if this is the key we are looking for...
                if check_unique_key:         # keep looking at all keys in 'd', to check if there is a conflict
                    if value is not None:    # here was already another value -> not unique
                        raise ValueError(f"There is a conflict (two or more) of key {key} in the dictionary. \n {d}",
                                         f"1. path: {path_to_value} \n"
                                         f"2. path: {current_path}")
                    path_to_value = deepcopy(current_path)  # deepcopy because lists are mutable
                    value = v                # set to final value
                else:
                    # if the integrity is not checked, return immediately the key and path
                    if check_final_leaf and isinstance(v, dict):
                        raise ValueError(f"Value to return for key {key} is not a leaf (i.e. value) but a "
                                         f"sub-dictionary.")
                    return v, deepcopy(current_path)

            if isinstance(v, dict):          # fill stack with more subdicts
                stack.append(iter(v.items()))
                break
            else:                            # remove last key again from list
                current_path = current_path[:-1]
        else:
            # if/else statement: if loop ended normally then run this: remove last key from path and remove this
            # entry from the stack
            current_path = current_path[:-1]
            stack.pop()

    if value is None:
        raise ValueError(f"Key {key} not found. \n {d}")
    return value, path_to_value  # NOTE: there is another return in the loop, when check_integrity is False


def all_nested_keys(d: dict):
        """Returns all keys present in the dictionary."""

        all_keys = []
        stack = [iter(d.items())]
        while stack:
            for k, v in stack[-1]:
                all_keys.append(k)
                if isinstance(v, dict):
                    stack.append(iter(v.items()))
                    break
            else:
                stack.pop()

        return all_keys


def get_dict_value_keylist(d: dict, path: list, last_key: str):
    return reduce(dict.__getitem__, path, d)[last_key]


def set_dict_value_keylist(d: dict, path: list, last_key: str, value):
    reduce(dict.__getitem__, path, d)[last_key] = value
    return d


def change_value(d: dict, path: list, last_key: str, value):
    try:
        exist_val = get_dict_value_keylist(d, path, last_key)
    except KeyError:
        raise KeyError(f"Cannot change value because path {path+last_key} does not exist.")

    if isinstance(exist_val, dict):
        raise ValueError("Cannot values to sub-directories!")

    # Security: if there is a completely new type (which cannot be casted) then throw error
    if type(exist_val) != type(value):

        # check for numbers...
        if isinstance(exist_val, numbers.Number) and isinstance(value, numbers.Number):

            # ignore cases, in case there are warppers around the float (such as from float <->_np.float64)
            if isinstance(exist_val, float) and isinstance(value, float) or \
                    isinstance(exist_val, int) and isinstance(value, int):
                pass
            else:  # print warning in cases where e.g. the existing value is an int and the new value is a double
                print(f"WARNING: key {last_key} at path {path} has type {type(exist_val)} but the new value has type "
                      f"{type(value)}. The value is not casted.")
        else:
            print(f"WARNING: There is a type casting from type {type(value)} (set value) to type {exist_val} "
                  f"(existing value)")
            try:
                value = type(exist_val)(value)  # try to cast, if it failes raise error
            except ValueError as e:
                print(f"Type-cast failed for key {last_key} at path {path}.")
                raise e

    return set_dict_value_keylist(d, path, last_key, value)


def change_existing_dict(d: dict, changes: dict):
    for k, v in changes.items():
        _, p = deep_dict_lookup(d, k)
        path, last_key = p[:-1], p[-1]
        d = change_value(d, path, last_key, v)
    return d


if __name__ == "__main__":
    d1 = {"a": {"b": 1, "c": {"x": 3}, "d": {"f": 3}}}
    # print(deep_dict_lookup(d, "x", True))

    print(change_existing_dict(d1, {"a|b": 3}))

    #print(deep_subdict(d, ["c"]))
    #print(abs_path_key(d, "a|c|x"))