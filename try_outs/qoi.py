#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import abc
import os
import typing

import pandas as pd

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class QuantityOfInterest(metaclass=abc.ABCMeta):

    def __init__(self, output_file, name):
        self.name = name
        self._output_file = output_file

    @abc.abstractmethod
    def read_and_extract_qoi(self, fp) -> typing.Union[float, pd.Series]:
        raise NotImplementedError("ABC method")


class EvacuationTime(QuantityOfInterest):

    def __init__(self, apply="mean", output_file=None):
        if output_file is None:
            output_file = "evacuationTimes.txt"
        name = "_".join(["evacTime", apply])
        super(EvacuationTime, self).__init__(output_file, name)

        assert apply in ["mean", "max"]
        self._apply = apply

    def _read_file(self, output_path):
        fp = os.path.join(output_path, self._output_file)
        return pd.read_csv(fp, delimiter=" ", index_col=0, header=0)

    def _extract_qoi(self, df: pd.DataFrame):
        if self._apply == "mean":
            return float(df.mean(axis=0))  # TODO: make routine in super class to have well defined casting
        else:
            return float(df.max(axis=0))

    def read_and_extract_qoi(self, fp):
        df = self._read_file(fp)
        return self._extract_qoi(df)


