#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import json
import os

import pandas as pd

# http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.ParameterSampler.html
from sklearn.model_selection import ParameterGrid, ParameterSampler
from try_outs.environment import EnvironmentManager
from try_outs.utils.dict_utils import *
from try_outs.utils.general import create_folder, remove_folder

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class ParameterVariation(object):

    def __init__(self, env_name):
        self._envname = env_name
        self._env_man = EnvironmentManager.set_by_env_name(env_name)
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

        try:  # check that the value is 'final' (i.e. not another sub-directory) and that the key is unique.
            deep_dict_lookup(scjson, key, check_final_leaf=True, check_unique_key=True)
        except ValueError as e:
            raise e  # re-raise Exception

        return True

    def _check_all_keys(self, scjson, keys):
        for k in keys:
            self._check_key(scjson, k)
        return True

    def _keys_of_paramgrid(self, grid: ParameterGrid):
        return grid.param_grid[0].keys()

    def add_sklearn_grid(self, grid: ParameterGrid):
        scjson = self._env_man.get_vadere_scenario_basis_file(sc_name=self._envname)  # corresponding scenario file
        self._check_all_keys(scjson, self._keys_of_paramgrid(grid))   # validate, that keys are valid
        self._points = self._add_points_df(points=list(grid))         # list creates all points described by the 'grid'
        return self.points

    @property
    def points(self):
        return self._points

    def iter(self):
        for i, row in self.points.iterrows():
            yield (i, dict(row))


class ScenarioVariationCreator(object):

    def __init__(self, scname: str, var: ParameterVariation):
        self._scname = scname
        self._scman = EnvironmentManager.set_by_env_name(self._scname)
        self._basis_scenario = self._scman.get_vadere_scenario_basis_file(self._scname)
        self._var = var

    def _create_new_vad_scenario(self, par: dict):
        return change_existing_dict(self._basis_scenario, changes=par)

    def _save_scenario(self, par_id, s):
        filename = "".join([str(par_id).zfill(10), ".scenario"])
        fp = os.path.join(self._scman.get_vadere_scenarios_folder(), filename)
        with open(fp, "w") as outfile:
            json.dump(s, outfile, indent=4)

    def _save_overview(self):
        filename = "points_overview.csv"
        fp = os.path.join(self._scman.get_vadere_scenarios_folder(), filename)
        self._var.points.to_csv(fp)

    def generate_scenarios(self):
        target_path = self._scman.get_vadere_scenarios_folder()

        # TODO: for now everytime it is removed an inserted again, but later it may be better to add and keep stuff...
        remove_folder(target_path)
        create_folder(target_path)

        for par_id, par_changes in self._var.iter():
            new_scenario = self._create_new_vad_scenario(par_changes)
            self._save_scenario(par_id, new_scenario)
        self._save_overview()


if __name__ == "__main__":
    di = {"speedDistributionStandardDeviation": [0.0, 0.1, 0.2]}
    grid = ParameterGrid(param_grid=di)

    pv = ParameterVariation(env_name="corner")
    pv.add_dict_grid(di)

    vc = ScenarioVariationCreator("corner", pv)
    vc.generate_scenarios()
