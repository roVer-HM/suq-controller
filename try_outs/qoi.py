#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import abc
import os
import typing

import pandas as pd

from try_outs.utils.general import cast_series_if_possible

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class QuantityOfInterest(metaclass=abc.ABCMeta):

    # TODO: maybe it is good to have here the Environment manager, this gives access to all the fixed settings

    def __init__(self, output_file, name):
        self.name = name
        self._output_file = output_file

    @abc.abstractmethod
    def read_and_extract_qoi(self, output_path, **kwargs) -> typing.Union[float, pd.Series]:
        raise NotImplementedError("ABC method")

    def _filepath(self, output_path):
        return os.path.join(output_path, self._output_file)

    def _read_csv(self, output_path):
        fp = self._filepath(output_path)
        df = pd.read_csv(fp, delimiter=" ", index_col=0, header=0)
        return cast_series_if_possible(df)


class PedestrianEvacuationTimeProcessor(QuantityOfInterest):

    def __init__(self, apply="mean", output_file=None):
        if output_file is None:
            output_file = "evacuationTimes.txt"

        assert apply in ["mean", "max"]
        self._apply = apply

        name = "_".join(["evacTime", self._apply])

        super(PedestrianEvacuationTimeProcessor, self).__init__(output_file, name)

    def _apply_homogenization(self, data: pd.Series):
        if self._apply == "mean":
            return float(data.mean())
        else:
            return float(data.max())

    def read_and_extract_qoi(self, output_path, **kwargs):
        df = self._read_csv(output_path)
        return self._apply_homogenization(df)


class AreaDensityVoronoiProcessor(QuantityOfInterest):

    def __init__(self, output_file=None):
        if output_file is None:
            output_file = "voronoi_density.txt"

        super(AreaDensityVoronoiProcessor, self).__init__(output_file, name="voronoi_density")

    def read_and_extract_qoi(self, output_path, **kwargs):
        data = self._read_csv(output_path)
        return data




