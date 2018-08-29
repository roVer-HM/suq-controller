#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import abc
import os
import typing

import pandas as pd

from try_outs.utils.general import cast_series_if_possible
from try_outs.configuration import EnvironmentManager

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class QuantityOfInterest(metaclass=abc.ABCMeta):

    # TODO: maybe it is good to have here the Environment manager, this gives access to all the fixed settings

    def __init__(self, em: EnvironmentManager, proc_name: str, qoi_name: str):
        self.name = qoi_name

        self._em = em
        self._proc_name = proc_name
        self._proc_config = self._get_proc_config()
        self._proc_id = self._proc_config["id"]
        self._outputfile_name = self._get_outout_filename()

    @abc.abstractmethod
    def read_and_extract_qoi(self, output_path, **kwargs) -> typing.Union[float, pd.Series]:
        raise NotImplementedError("ABC method")

    def _get_all_proc_writers(self):
        return self._em.get_value_basis_file(key="processWriters")[0]

    def _get_proc_config(self):
        procwriter_json = self._get_all_proc_writers()
        procs_list = procwriter_json["processors"]

        return_cfg = None
        for d in procs_list:
            if d["type"] == self._proc_name:
                if return_cfg is None:
                    return_cfg = d
                else:
                    raise RuntimeError("The processor has to be unique to avoid confusion which processor to use for "
                                       "the QoI.")
        return return_cfg


    def _get_outout_filename(self):
        procwriter_json = self._get_all_proc_writers()
        files = procwriter_json["files"]

        file_cfg = None
        for file in files:
            procs_list = file["processors"]
            if self._proc_id in procs_list:
                if file_cfg is None:
                    assert len(procs_list) == 1, "For now only single procs are allowed, this may be relaxed in future"
                    file_cfg = file
                else:
                    raise RuntimeError("The processor has to be unique to avoid confusion which processor to use for "
                                       "the QoI.")
        return file_cfg["filename"]

    def _filepath(self, output_path):
        return os.path.join(output_path, self._outputfile_name)

    def _read_csv(self, output_path):
        fp = self._filepath(output_path)
        df = pd.read_csv(fp, delimiter=" ", index_col=0, header=0)
        return cast_series_if_possible(df)


class PedestrianEvacuationTimeProcessor(QuantityOfInterest):

    def __init__(self, em: EnvironmentManager, apply="mean"):

        assert apply in ["mean", "max"]
        self._apply = apply

        proc_name = "org.vadere.simulator.projects.dataprocessing.processor.PedestrianEvacuationTimeProcessor"
        qoi_name = "_".join(["evacTime", self._apply])

        super(PedestrianEvacuationTimeProcessor, self).__init__(em, proc_name, qoi_name)

    def _apply_homogenization(self, data: pd.Series):
        if self._apply == "mean":
            return float(data.mean())
        else:
            return float(data.max())

    def read_and_extract_qoi(self, output_path, **kwargs):
        df = self._read_csv(output_path)
        return self._apply_homogenization(df)


class AreaDensityVoronoiProcessor(QuantityOfInterest):

    def __init__(self, em: EnvironmentManager):
        proc_name = "org.vadere.simulator.projects.dataprocessing.processor.AreaDensityVoronoiProcessor"

        super(AreaDensityVoronoiProcessor, self).__init__(em, proc_name, "voronoi_density")

    def read_and_extract_qoi(self, output_path, **kwargs):
        data = self._read_csv(output_path)
        return data




