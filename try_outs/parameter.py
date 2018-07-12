#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import pandas as pd

from copy import deepcopy   # often better to deepcopy dicts

# http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.ParameterSampler.html
from sklearn.model_selection import ParameterGrid, ParameterSampler
from try_outs.scenario import ScenarioManager

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


# TODO: generate all scenarios files according to ParameterVariation (maybe better in an outer method, not in ParameterVariation itsel
# TODO: put all the dictionay method in a helper module/class, as these will be needed again...

class ParameterVariation(object):

    def __init__(self, sc_name):
        self._scname = sc_name
        self._scman = ScenarioManager.setscname(sc_name)
        self._points = pd.DataFrame()

    def _deep_dict_lookup(self, d: dict, key: str):
        """Return a value corresponding to the specified key in the (possibly
        nested) dictionary d. If there is no item with that key raise ValueError.
        """
        # "Stack of Iterators" pattern: http://garethrees.org/2016/09/28/pattern/
        # https://stackoverflow.com/questions/14962485/finding-a-key-recursively-in-a-dictionary

        stack = [iter(d.items())]
        while stack:
            for k, v in stack[-1]:
                if k == key:
                    return v
                elif isinstance(v, dict):
                    stack.append(iter(v.items()))
                    break
            else:
                stack.pop()
        raise ValueError(f"Key {key} not found")

    def _add_points_df(self, points):
        # NOTE: it may be required to generalize 'points' definition, at the moment it is assumed to be a list(grid),
        # where 'grid' is a ParameterGrid of scikit-learn

        df = pd.concat([self._points, pd.DataFrame(points)], ignore_index=True, axis=0)
        df.index.name = "par_id"
        df.columns.name = "parameters"
        return df

    def add_dict_grid(self, d: dict):
        return self.add_sklearn_grid(ParameterGrid(param_grid=d))

    def _all_nested_keys(self, d):
        """Return a value corresponding to the specified key in the (possibly
        nested) dictionary d. If there is no item with that key raise ValueError.
        """
        # "Stack of Iterators" pattern: http://garethrees.org/2016/09/28/pattern/
        # https://stackoverflow.com/questions/14962485/finding-a-key-recursively-in-a-dictionary

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

    def _check_key(self, scjson, key):
        # 1. Check for precise description (no multiple keys available...)
        d = deepcopy(scjson)
        last_key = key
        if "|" in key:  # | is the separater sign -- # TODO: possibly define this somewhere...
            key_chain = key.split("|")
            for ky in key_chain[:-1]:
                d = self._deep_dict_lookup(d, ky)
                assert isinstance(d, dict)
            last_key = key_chain[-1]
        if self._all_nested_keys(d).count(last_key) != 1:
            raise ValueError(f"Key {key} is not precise, because there are multiple occurences of {last_key} in \n"
                             f"{d}")

        # 2. Check: Value is not another sub-dict
        val = self._deep_dict_lookup(d, last_key)
        if isinstance(val, dict):
            raise ValueError(f"Invalid key identifier: '{last_key}' in description {key} is not a final value, but "
                             f"another sub-dict.")
        return True

    def _check_all_keys(self, scjson, keys):
        for k in keys:
            self._check_key(scjson, k)
        return True

    def _keys_of_paramgrid(self, grid: ParameterGrid):
        return grid.param_grid[0].keys()

    def add_sklearn_grid(self, grid: ParameterGrid):
        scjson = self._scman.get_scenario_file(sc_name=self._scname)  # corresponding scenario file
        self._check_all_keys(scjson, self._keys_of_paramgrid(grid))   # validate, that keys are valid
        self._points = self._add_points_df(points=list(grid))         # list creates all points described by the 'grid'
        return self.points

    @property
    def points(self):
        return self._points

    def iter(self):
        for i, row in self.points.iterrows():
            yield (i, dict(row))

def _generate_scenarios(var: ParameterVariation):
    pass


if __name__ == "__main__":
    d = {"bounds|x": [1.1, 1.2, 1.3],
         "speedDistributionStandardDeviation": [0.0, 0.1, 0.2]}
    grid = ParameterGrid(param_grid=d)

    pv = ParameterVariation(sc_name="chicken")
    pv.add_dict_grid(d)

    for k in pv.iter():
        print(k)


    #ParameterVariation.add_dict_grid(d)
