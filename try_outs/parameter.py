#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import json
import os

import pandas as pd

from copy import deepcopy   # often better to deepcopy dicts

# http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.ParameterSampler.html
from sklearn.model_selection import ParameterGrid, ParameterSampler
from try_outs.scenario import ScenarioManager
from try_outs.utils.dict_utils import *

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

    def _add_points_df(self, points):
        # NOTE: it may be required to generalize 'points' definition, at the moment it is assumed to be a list(grid),
        # where 'grid' is a ParameterGrid of scikit-learn

        df = pd.concat([self._points, pd.DataFrame(points)], ignore_index=True, axis=0)
        df.index.name = "par_id"
        df.columns.name = "parameters"
        return df

    def add_dict_grid(self, d: dict):
        return self.add_sklearn_grid(ParameterGrid(param_grid=d))

    def _check_key(self, scjson, key):
        # 1. Check for precise description (no multiple keys available...)
        d = deepcopy(scjson)  # better to deepcopy the scjson, because dicts are mutable

        # the chain describes the keys (looked up deep in dict) in given order
        # last_key describes the key the user wants to change
        key_path, last_key = key_split(key)

        d, _ = deep_subdict(d, key_path)

        try:
            deep_dict_lookup(d, last_key, check_integrity=True)
        except ValueError as e:
            raise e  # re-raise Exception

        # 2. Check: Value is not another sub-dict
        val = deep_dict_lookup(d, last_key)
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
        scjson = self._scman.get_vadere_scbasis_file(sc_name=self._scname)  # corresponding scenario file
        self._check_all_keys(scjson, self._keys_of_paramgrid(grid))   # validate, that keys are valid
        self._points = self._add_points_df(points=list(grid))         # list creates all points described by the 'grid'
        return self.points

    @property
    def points(self):
        return self._points

    def iter(self):
        for i, row in self.points.iterrows():
            yield (i, dict(row))


class VariationCreator(object):

    def __init__(self, scname: str, var: ParameterVariation):
        self._scname = scname
        self._scman = ScenarioManager.setscname(self._scname)
        self._basis_scenario = self._scman.get_vadere_scbasis_file(self._scname)
        self._var = var

    def _create_new_vad_scenario(self, par: dict):
        return change_existing_dict(self._basis_scenario, changes=par)

    def _save_scenario(self, par_id, s):
        filename = "".join([str(par_id).zfill(10), ".scenario"])
        fp = os.path.join(self._scman.get_scvadere_folder(self._scname), filename)
        with open(fp, "w") as outfile:
            json.dump(s, outfile, indent=4)

    def generate_scenarios(self):
        target_path = self._scman.get_scvadere_folder(self._scname)

        # TODO: for now everytime it is removed an inserted again, but later it may be better to add and keep stuff...
        import os
        files = os.listdir(target_path)
        for f in files:
            os.remove(os.path.join(target_path, f))

        for par_id, par_changes in self._var.iter():
            new_scenario = self._create_new_vad_scenario(par_changes)
            self._save_scenario(par_id, new_scenario)


if __name__ == "__main__":
    d = {"bounds|x": [9999, 1.2, 1.3],
         "speedDistributionStandardDeviation": [5555, 0.1, 0.2]}
    grid = ParameterGrid(param_grid=d)

    pv = ParameterVariation(sc_name="chicken")
    pv.add_dict_grid(d)

    vc = VariationCreator("chicken", pv)
    vc.generate_scenarios()


