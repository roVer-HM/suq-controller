#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import abc

import pandas as pd
import numpy as np

from typing import List

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


class ParameterVariation(metaclass=abc.ABCMeta):

    MULTI_IDX_LEVEL0_PAR = "Parameter"
    MULTI_IDX_LEVEL0_LOC = "Location"
    ROW_IDX_NAME = "par_id"  # TODO: think of defining the 'default' data parts somewhere else...

    def __init__(self, env_man: EnvironmentManager, scenario_changes: ):
        self._env_man = env_man
        self._points = pd.DataFrame()

    @property
    def points(self):
        return self._points

    def reset_env_man(self, env_man: EnvironmentManager):
        """The environment manager is resetted when it is used remotely on a server (i.e. with other paths)."""
        self._env_man = env_man

    def _add_points_df(self, points: List[dict]):
        # NOTE: it may be required to generalize 'points' definition, at the moment it is assumed to be a list(grid),
        # where 'grid' is a ParameterGrid of scikit-learn

        df = pd.concat([self._points, pd.DataFrame(points)], ignore_index=True, axis=0)
        df.index.name = ParameterVariation.ROW_IDX_NAME

        df.columns = pd.MultiIndex.from_product([[ParameterVariation.MULTI_IDX_LEVEL0_PAR], df.columns])
        self._points = df

    def _check_selected_keys(self, keys):
        scjson = self._env_man.get_vadere_scenario_basis_file()
        for key in keys:
            try:  # check that the value is 'final' (i.e. not another sub-directory) and that the key is unique.
                deep_dict_lookup(scjson, key, check_final_leaf=True, check_unique_key=True)
            except ValueError as e:
                raise e  # re-raise Exception
        return True

    def _create_new_vadere_scenario(self, par: dict):
        basis_scenario = self._env_man.get_vadere_scenario_basis_file()
        return change_existing_dict(basis_scenario, changes=par)

    def _save_vadere_scenario(self, par_id, s):
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
            fp = self._save_vadere_scenario(par_id, new_scenario)
            vars.append(self._vars_object(par_id, fp))
        return vars

    def nr_par_variations(self):
        return self._points.shape[0]

    def par_iter(self):
        for i, row in self._points[ParameterVariation.MULTI_IDX_LEVEL0_PAR].iterrows():
            yield (i, dict(row))


class FullGridSampling(ParameterVariation):

    def __init__(self, env_man: EnvironmentManager):
        super(FullGridSampling, self).__init__(env_man)
        self._added_grid = False

    def _keys_of_paramgrid(self, grid: ParameterGrid):
        return grid.param_grid[0].keys()

    def add_dict_grid(self, d: dict):
        return self.add_sklearn_grid(ParameterGrid(param_grid=d))

    def add_sklearn_grid(self, grid: ParameterGrid):
        if self._added_grid:
            print("WARNING: Grid has already been added, can only add once.")
        else:
            self._check_selected_keys(self._keys_of_paramgrid(grid))   # validate, that keys are valid
            self._add_points_df(points=list(grid))         # list creates all points described by the 'grid'
        return self._points


class RandomSampling(ParameterVariation):

    # TODO: Check out ParameterSampler in scikit learn which I think combines random sampling with a grid.

    def __init__(self, env_man: EnvironmentManager):
        super(RandomSampling, self).__init__(env_man=env_man)
        self._add_parameters = True
        self.dists = dict()

    def add_parameter(self, par: str, dist: np.random, **dist_pars: dict):
        assert self._add_parameters, "The grid was already generated. For now it is not allowed to add more parameters " \
                                     "afterwards"
        self.dists[par] = {"dist": dist, "dist_pars": dist_pars}

    def _create_distribution_samples(self, nr_samples):

        samples = list()
        for i in range(nr_samples):
            samples.append({})

        for d in self.dists.keys():

            dist_args = deepcopy(self.dists[d]["dist_pars"])
            dist_args["size"] = nr_samples

            try:
                outcomes = self.dists[d]["dist"](**dist_args)
            except:
                raise RuntimeError(f"Distribution {d} failed to sample. Every distribution has to support the keyword"
                                   f" 'size'. It is recommended to use distributions from numpy: "
                                   f"https://docs.scipy.org/doc/numpy-1.13.0/reference/routines.random.html")

            for i in range(nr_samples):
                samples[i][d] = outcomes[i]

        return samples

    def create_grid(self, nr_samples=100):
        self._add_parameters = False
        self._check_selected_keys(self.dists.keys())
        samples = self._create_distribution_samples(nr_samples)
        self._add_points_df(samples)


class BoxSampling(ParameterVariation):

    def __init__(self, env_man: EnvironmentManager):
        super(BoxSampling, self).__init__(env_man)
        self._edges = None

    def _create_box_points(self, par, test_p):
        return [{par: test_p[i]} for i in range(len(test_p))]

    def create_grid(self, par, lb, rb, nr_boxes, nr_testf):
        """NOTE: Currently only 1D parameter is supported..."""

        self._edges = np.linspace(lb, rb, nr_boxes+1)  # +1 bc. edges+1 = nr_boxes when the parameter
        self._box_width = self._edges[1] - self._edges[0]  # the linspace guarantees equidistant box-domains

        all_points = list()

        boxid_vector = np.zeros(nr_boxes * nr_testf)

        for box in range(nr_boxes):
            test_p = np.linspace(self._edges[box], self._edges[box+1], nr_testf)
            boxid_vector[box*nr_testf: (box+1)*nr_testf] = int(box)
            all_points += self._create_box_points(par, test_p)

        self._add_points_df(all_points)
        self._points["BoxID", ""] = boxid_vector


if __name__ == "__main__":
    di = {"speedDistributionStandardDeviation": [0.0, 0.1, 0.2]}

    em = EnvironmentManager("corner")

    pv = BoxSampling(em)
    pv.create_grid("speedDistributionMean", 0, 1, 100, 100)

    print(pv.points)

    pv = RandomSampling(em)
    pv.add_parameter("speedDistributionStandardDeviation", np.random.normal)
    pv.add_parameter("speedDistributionMean", np.random.normal)
    pv.create_grid()

    print(pv._points)
