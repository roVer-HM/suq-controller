#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

from copy import deepcopy
from functools import reduce

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


def deep_dict_lookup(d: dict, key: str, check_integrity=False):
    """Return a value corresponding to the specified key in the (possibly
    nested) dictionary d. If there is no item with that key raise ValueError.
    """
    # "Stack of Iterators" pattern: http://garethrees.org/2016/09/28/pattern/
    # https://stackoverflow.com/questions/14962485/finding-a-key-recursively-in-a-dictionary
    value = None

    current_path = []
    path_to_value = None

    stack = [iter(d.items())]
    while stack:
        for k, v in stack[-1]:
            current_path.append(k)
            if k == key:
                if check_integrity:  # keep looking at all keys, if there is a conflict, return error
                    if value is not None: # here was already another value -> not unique
                        raise ValueError(f"There is a conflict (two or more) of key {key} in the dictionary. \n {d}")
                    path_to_value = deepcopy(current_path)  # deepcopy becuase is mutable
                    value = v
                else:
                    return v, path_to_value

            elif isinstance(v, dict):
                stack.append(iter(v.items()))
                break
            else:
                current_path.remove(k)
        else:
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


def deep_subdict(d: dict, keys: list):
    """Returns a subdict, where the path is described by 'keys'. At each level the keys are looked up deep."""
    path = []

    if not keys:  # -> keys is empty
        return d, path

    for k in keys:
        d, p = deep_dict_lookup(d, k, True)
        path += p
        assert isinstance(d, dict)
    return d, path


def key_split(key: str):
    path = key.split("|")
    return path[:-1], path[-1]


def abs_path_key(d: dict, key: str):
    desc_keys, last_key = key_split(key)

    if desc_keys:
        d, path = deep_subdict(d, desc_keys)
    else:
        _, path = deep_dict_lookup(d, key, check_integrity=True)
        path.remove(last_key)

    if all_nested_keys(d).count(last_key) != 1:
        raise ValueError("Wrong description of key.")

    return path, last_key


def change_value(d: dict, path: str, last_key: str, value):
    try:
        exist_val = reduce(dict.__getitem__, path, d)[last_key]
    except KeyError as e:
        raise KeyError(f"Cannot change value because path {path+last_key} does not exist.")

    if isinstance(exist_val, dict):
        raise ValueError("Cannot values to sub-directories!")

    #if type(exist_val) != type(value):
        # TODO this can be relaxed a bit in the future, e.g. allow ints when doubles are required (-> cast if possible)
    #    raise ValueError(f"Inferring valid types from existing: \n Types of existing value {type(exist_val)} and "
    #                     f"new value {type(value)} do not match!")

    reduce(dict.__getitem__, path, d)[last_key] = value
    return d


def change_existing_dict(d: dict, changes: dict):
    for k, v in changes.items():
        path, last_key = abs_path_key(d, k)
        d = change_value(d, path, last_key, v)
    return d

if __name__ == "__main__":
    d = {"a": {"b": 1, "c": {"x": 3}, "d": {"f": 3}}}
    # print(deep_dict_lookup(d, "x", True))

    print(change_existing_dict(d, {"a|b": 3}))

    #print(deep_subdict(d, ["c"]))
    #print(abs_path_key(d, "a|c|x"))