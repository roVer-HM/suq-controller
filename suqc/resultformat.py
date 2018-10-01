#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import pandas as pd

from typing import List

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class ParameterResult(object):

    @staticmethod
    def concat_parameter_results(data: List["ParameterResult"]):
        return pd.concat([i.data for i in data])

    def __init__(self, par_id, data, qoi_name):

        self.par_id = par_id
        self._qoi_name = qoi_name

        # that is usually time (which can be actual 'time' or 'timeStep')
        # Depending on other DataProcessors in Vadere this may not always make sense...
        self._kind = data.index.name

        if isinstance(data, pd.Series):
            self._data = self._insert_data_series(data)
        elif isinstance(data, pd.DataFrame):
            self._data = self._insert_data_df(data)
        else:
            raise Exception()

    @property
    def data(self):
        return self._data

    def _col_multi_index(self, nr_vals, idx_cols):
        # Note. idx_cols are often numeric as they represent for example time.
        lvl0 = [self.qoi_col_name()] * nr_vals
        lvl1 = idx_cols
        return pd.MultiIndex.from_arrays([lvl0, lvl1])

    def _insert_data_df(self, data):
        assert isinstance(data, pd.DataFrame)
        df = data.T   # assumes that time is in index, this may not be true for all data processors?
        df.index = pd.MultiIndex.from_product(([self.par_id], df.index.values))
        df.columns = self._col_multi_index(df.shape[1], df.columns.values)
        return df

    def _insert_data_series(self, data):
        assert isinstance(data, pd.Series)
        df = pd.DataFrame(data).T
        df.index = [self.par_id]  # list because must be called with a collection fo some kind
        df.columns = self._col_multi_index(df.shape[1], df.columns.values)
        return df

    @DeprecationWarning
    @classmethod
    def series_extracted_vadere_results(cls, par_id, series, qoi_name):
        series.name = par_id
        kind = series.index.name
        series.index.name = ""
        return ParameterResult(par_id, series, qoi_name)

    def qoi_col_name(self):
        if self._kind is None:
            return "_".join(["QoI", self._qoi_name, "scalar"])
        else:
            return "_".join(["QoI", self._qoi_name, self._kind])
