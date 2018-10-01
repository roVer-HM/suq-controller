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

    def __init__(self):
        self._points = pd.DataFrame()

    @property
    def points(self):
        return self._points

    def _add_dict_points(self, points: List[dict]):
        # NOTE: it may be required to generalize 'points' definition, at the moment it is assumed to be a list(grid),
        # where 'grid' is a ParameterGrid of scikit-learn

        df = pd.concat([self._points, pd.DataFrame(points)], ignore_index=True, axis=0)
        df.index.name = ParameterVariation.ROW_IDX_NAME

        df.columns = pd.MultiIndex.from_product([[ParameterVariation.MULTI_IDX_LEVEL0_PAR], df.columns])
        self._points = df

    def _add_df_points(self, points: pd.DataFrame):
        self._points = points

    def check_selected_keys(self, scenario: dict):
        keys = self._points[ParameterVariation.MULTI_IDX_LEVEL0_PAR].columns

        for k in keys:
            try:  # check that the value is 'final' (i.e. not another sub-directory) and that the key is unique.
                deep_dict_lookup(scenario, k, check_final_leaf=True, check_unique_key=True)
            except ValueError as e:
                raise e  # re-raise Exception
        return True

    def nr_par_variations(self):
        return self._points.shape[0]

    def par_iter(self):
        for i, row in self._points[ParameterVariation.MULTI_IDX_LEVEL0_PAR].iterrows():
            yield (i, dict(row))


class FullGridSampling(ParameterVariation):

    def __init__(self):
        super(FullGridSampling, self).__init__()
        self._added_grid = False

    def _keys_of_paramgrid(self, grid: ParameterGrid):
        return grid.param_grid[0].keys()

    def add_dict_grid(self, d: dict):
        return self.add_sklearn_grid(ParameterGrid(param_grid=d))

    def add_sklearn_grid(self, grid: ParameterGrid):
        if self._added_grid:
            print("WARNING: Grid has already been added, can only add once.")
        else:
            self._add_dict_points(points=list(grid))         # list creates all points described by the 'grid'
        return self._points


class RandomSampling(ParameterVariation):

    # TODO: Check out ParameterSampler in scikit learn which I think combines random sampling with a grid.

    def __init__(self):
        super(RandomSampling, self).__init__()
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
        samples = self._create_distribution_samples(nr_samples)
        self._add_dict_points(samples)


class BoxSampling(ParameterVariation):

    def __init__(self):
        super(BoxSampling, self).__init__()
        self._edges = None

    def _create_box_points(self, par, test_p):
        return [{par: test_p[i]} for i in range(len(test_p))]

    def _generate_interior_start(self, edges, nr_testf):

        boxes = len(edges)-1
        arr = np.zeros(boxes * nr_testf)

        for i in range(boxes):
            s, e = edges[i:i+2]
            arr[i*nr_testf: i*nr_testf+nr_testf] = np.linspace(s, e, nr_testf+2)[1:-1]
        return arr

    def _get_idx(self, val, dim):
        return int(np.floor((val-self._edges[dim][0]) / self._box_width[dim]))

    def _get_box(self, row):

        vals = row.values

        idx_x = self._get_idx(vals[0], 0)
        if len(vals) == 1:
            idx_y = 0
            idx_z = 0
        elif len(vals) == 2:
            idx_y = self._get_idx(vals[1], 1)
            idx_z = 0
        else:
            idx_y = self._get_idx(vals[1], 1)
            idx_z = self._get_idx(vals[2], 2)

        box = idx_x + idx_y * (self._nr_boxes[0]) + idx_z * (self._nr_boxes[0] * self._nr_boxes[1])
        return box

    def create_grid(self, par, lb, rb, nr_boxes, nr_testf):

        if isinstance(par, str):
            par = [par, None, None]

        if isinstance(lb, (float, int)):
            lb = [lb, 0, 0]

        if isinstance(rb, (float, int)):
            rb = [rb, 0, 0]

        if isinstance(nr_boxes, int):
            nr_boxes = [nr_boxes, 0, 0]

        if isinstance(nr_testf, int):
            nr_testf = [nr_testf, 0, 0]

        assert len(lb) == len(rb) == len(nr_boxes) == len(nr_testf) == 3

        self._nr_boxes = nr_boxes  # TODO: possible bring this in constructor

        self._edges = dict()
        self._box_width = dict()  # same initial setting

        for i in range(3):
            if par[i] is not None:
                # +1 bc. edges+1 = nr_boxes when the parameter
                self._edges[i] = np.linspace(lb[i], rb[i], nr_boxes[i]+1)

                # the linspace guarantees equidistant box-domains
                self._box_width[i] = self._edges[i][1] - self._edges[i][0]

        all_points = list()


        # ^ y
        # |
        # |5 | 6 | 7 | 8 |
        # |1 | 2 | 3 | 4 |
        #  _________________>  x
        # o z (looking from above)
        #
        # If there is a 3rd parameter (z) the next slice starts on top of this (bottom-up)

        x_pos, y_pos, z_pos = [None, None, None]

        if par[0] is not None:
            x_pos = self._generate_interior_start(edges=self._edges[0], nr_testf=nr_testf[0])

        if par[1] is not None:
            y_pos = self._generate_interior_start(edges=self._edges[1], nr_testf=nr_testf[1])

        if par[2] is not None:
            z_pos = self._generate_interior_start(edges=self._edges[2], nr_testf=nr_testf[2])

        mesh = np.meshgrid(x_pos, y_pos, z_pos, copy=True, indexing="xy")

        df_x, df_y, df_z = [None, None, None]

        df_x = pd.DataFrame(mesh[0].ravel(), columns=[par[0]])

        if par[1] is not None:
            df_y = pd.DataFrame(mesh[1].ravel(), columns=[par[1]])

        if par[2] is not None:
            df_z = pd.DataFrame(mesh[2].ravel(), columns=[par[2]])

        df_final = pd.concat([df_x, df_y, df_z], axis=1)
        df_final.columns = pd.MultiIndex.from_product(
            [[ParameterVariation.MULTI_IDX_LEVEL0_PAR], df_final.columns.values])
        df_final.index.name = ParameterVariation.ROW_IDX_NAME

        df_final["boxid"] = df_final.T.apply(self._get_box)

        self._add_df_points(points=df_final)

        print(self._points)

if __name__ == "__main__":
    di = {"speedDistributionStandardDeviation": [0.0, 0.1, 0.2]}

    pd.options.display.max_columns = 4

    em = EnvironmentManager("corner")

    pv = BoxSampling()
    pv.create_grid(["speedDistributionStandardDeviation", "speedDistributionMean", "minimumSpeed"], [0, 1, 2], [1, 2, 3], [2, 2, 2], [2, 2, 2])





    #pv = FullGridSampling()
    #pv.add_dict_grid({"speedDistributionStandardDeviation": [0.1, 0.2, 0.3, 0.4]})
    #print(pv.points)

    # pv = RandomSampling(em)
    # pv.add_parameter("speedDistributionStandardDeviation", np.random.normal)
    # pv.add_parameter("speedDistributionMean", np.random.normal)
    # pv.create_grid()
    #
    # print(pv._points)
