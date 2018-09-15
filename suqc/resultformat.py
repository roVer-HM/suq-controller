#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import numpy as np
import pandas as pd

from typing import List

from suqc.parameter import ParameterVariation

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class ParameterResult(object):

    def __init__(self, par_id, data, qoi_name, kind=None):
        self.par_id = par_id
        self.nr_vals = data.shape[0]

        self._qoi_name = qoi_name
        self._kind = kind
        self._data = data

    @property
    def data(self):
        # add the multiindex, to be able to insert it into the final ResultDF with guarantee of correct cols
        # DataFrame
        idx = self.get_multi_index()
        data = self._data.copy(deep=True)
        data.index = idx
        return data

    @classmethod
    def from_extracted_vadere_results(cls, par_id, vals, qoi_name):
        vals.name = par_id
        kind = vals.index.name
        vals.index.name = ""
        return ParameterResult(par_id, vals, qoi_name, kind)

    def qoi_col_name(self):
        if self._kind is None:
            return "_".join(["QoI", self._qoi_name, "scalar"])
        else:
            return "_".join(["QoI", self._qoi_name, self._kind])

    def get_multi_index(self):
        lvl0 = [self.qoi_col_name()] * self.nr_vals
        lvl1 = self._data.index
        return pd.MultiIndex.from_arrays([lvl0, lvl1])


class ResultDF(object):

    def __init__(self, par_var: ParameterVariation):
        self._df: pd.DataFrame = par_var.points

    @property
    def data(self):
        return self._df

    def _is_first_insert(self, result):
        # in the first [0] twice, because it is a list --> so I get the firs element of the list to check if it is in
        # the list of current columns
        return not result.get_multi_index().levels[0][0] in self._df.columns.levels[0]

    def _insert_qoi_result(self, result: ParameterResult):
        self._df.loc[result.par_id, result.get_multi_index()] = result.data

    def _insert_inital_qoi(self, vals: ParameterResult):
        # TODO: at the moment assumes that vals is pd.Series
        cols = vals.get_multi_index()

        # Need to add another level in self._df
        init_df = pd.DataFrame(np.nan, index=self._df.index, columns=cols)
        self._df = pd.concat([self._df, init_df], axis=1)
        self._insert_qoi_result(vals)

    def add_result(self, result: ParameterResult):
        if self._is_first_insert(result):
            self._insert_inital_qoi(result)
        else:
            self._insert_qoi_result(result)

    def add_multi_results(self, results: List[ParameterResult]):
        for r in results:
            self.add_result(r)
