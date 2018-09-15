#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import pandas as pd
import numpy as np

# http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.ParameterSampler.html
from sklearn.model_selection import ParameterGrid, ParameterSampler
from suqc.configuration import EnvironmentManager
from suqc.utils.dict_utils import *
from suqc.utils.general import create_folder, remove_folder

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class ParameterVariation(object):

    MULTI_IDX_LEVEL0_PAR = "Parameter"
    MULTI_IDX_LEVEL0_LOC = "Location"
    ROW_IDX_NAME = "par_id"  # TODO: think of defining the 'default' data parts somewhere else...


    def __init__(self, env_man: EnvironmentManager):
        self._env_man = env_man
        self._points = pd.DataFrame()

    @property
    def points(self):
        return self._points

    def _add_points_df(self, points):
        # NOTE: it may be required to generalize 'points' definition, at the moment it is assumed to be a list(grid),
        # where 'grid' is a ParameterGrid of scikit-learn

        df = pd.concat([self._points, pd.DataFrame(points)], ignore_index=True, axis=0)
        df.index.name = ParameterVariation.ROW_IDX_NAME

        df.columns = pd.MultiIndex.from_product([[ParameterVariation.MULTI_IDX_LEVEL0_PAR], df.columns])
        return df

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

    def _create_new_vadere_scenario(self, par: dict):
        basis_scenario = self._env_man.get_vadere_scenario_basis_file()
        return change_existing_dict(basis_scenario, changes=par)

    def _save_scenario(self, par_id, s):
        fp = self._env_man.save_scenario_variation(par_id, s)
        self._points.loc[par_id, ParameterVariation.MULTI_IDX_LEVEL0_LOC] = fp
        return fp

    def _vars_object(self, pid, fp):
        return {ParameterVariation.ROW_IDX_NAME: pid, "scenario_path": fp}

    def generate_vadere_scenarios(self):
        target_path = self._env_man.get_scenario_variation_path()

        remove_folder(target_path)
        create_folder(target_path)

        vars = list()
        for par_id, par_changes in self.par_iter():
            new_scenario = self._create_new_vadere_scenario(par_changes)
            fp = self._save_scenario(par_id, new_scenario)
            vars.append(self._vars_object(par_id, fp))
        return vars

    def add_dict_grid(self, d: dict):
        return self.add_sklearn_grid(ParameterGrid(param_grid=d))

    def add_sklearn_grid(self, grid: ParameterGrid):
        scjson = self._env_man.get_vadere_scenario_basis_file()        # corresponding scenario file
        self._check_all_keys(scjson, self._keys_of_paramgrid(grid))   # validate, that keys are valid
        self._points = self._add_points_df(points=list(grid))         # list creates all points described by the 'grid'
        return self._points

    def nr_par_variations(self):
        return self._points.shape[0]

    def par_iter(self):
        for i, row in self._points[ParameterVariation.MULTI_IDX_LEVEL0_PAR].iterrows():
            yield (i, dict(row))


if __name__ == "__main__":
    di = {"speedDistributionStandardDeviation": [0.0, 0.1, 0.2]}

    em = EnvironmentManager("corner")
    pv = ParameterVariation(em)
    pv.add_dict_grid(di)

    pv.generate_vadere_scenarios()
