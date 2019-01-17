#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import abc

import os

import pandas as pd
import numpy as np

from suqc.utils.dict_utils import deep_dict_lookup
from suqc.configuration import EnvironmentManager

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class FileDataInfo(object):

    # TODO: see also vadere issue #199, to include this information in the scenario
    map_outputtype2index = {"IdOutputFile": 1,
                            "LogEventOutputFile": 1,
                            "NotDataKeyOutputFile": 0,
                            "PedestrianIdOutputFile": 1,
                            "TimestepOutputFile": 1,
                            "TimestepPedestrianIdOutputFile": 2,
                            "TimestepPedestrianIdOverlapOutputFile": 3,
                            "TimestepPositionOutputFile": 3,
                            "TimestepRowOutputFile": 2}

    def __init__(self, process_file, processors):
        self.filename = process_file["filename"]
        self.output_key = process_file["type"].split(".")[-1]

        self.processors = processors  # not really needed yet, but maybe in future.

        try:
            self.nr_indices = self.map_outputtype2index[self.output_key]
        except KeyError:
            raise KeyError(f"Outputtype={self.output_key} not present in mapping. May have to be inserted manually in "
                           f"code. Check out Vadere Gitlab issue # 199.")

    @DeprecationWarning
    def _select_qoiname(self, processors):

        full_name = set([p["type"] for p in processors])

        if len(full_name) != 1:
            raise ValueError("Only equal types are allowed")

        # get the last identifier
        # e.g. org.vadere.simulator.projects.dataprocessing.outputfile.TimestepPedestrianIdOutputFile
        # to TimestepPedestrianIdOutputFile
        datakey = full_name.pop().split(".")[-1]

        return datakey


class QuantityOfInterest(metaclass=abc.ABCMeta):

    def __init__(self, requested_files, em: EnvironmentManager):

        assert isinstance(requested_files, (list, str))

        if isinstance(requested_files, str):
            requested_files = [requested_files]

        basis = em.get_vadere_scenario_basis_file()

        user_set_writers, _ = deep_dict_lookup(basis, "processWriters")
        process_files = user_set_writers["files"]
        processsors = user_set_writers["processors"]

        self.req_qois = self._requested_qoi(requested_files, process_files, processsors)

    def _requested_qoi(self, requested_files, process_files, processsors):

        req_qois = list()

        for pf in process_files:

            # TODO: This has to exactly match, maybe make more robust to allow without
            filename = pf["filename"]  # TODO: see issue #33

            if filename in requested_files:

                sel_procs = self._select_corresp_processors(pf, processsors)

                req_qois.append(FileDataInfo(process_file=pf, processors=sel_procs))

                requested_files.remove(filename)  # -> processed, list should be empty when leaving function

        if requested_files:  # has to be empty
            raise ValueError(f"The requested files {requested_files} are not set in the Vadere scenario: \n "
                             f"{process_files}")

        return req_qois

    def _select_corresp_processors(self, process_file, processors):
        proc_ids = process_file["processors"]

        selected_procs = list()

        # TODO: see issue #33
        for pid in proc_ids:
            found = False
            for p in processors:
                if pid == p["id"]:
                    selected_procs.append(p)

                    if not found:
                        found = True
                    else:
                        raise ValueError("The Vadere scenario is not correctly set up! There are two processors with "
                                         f"the id={pid} could not be ")

            if not found:
                raise ValueError(f"The Vadere scenario is not correctly set up! Processor id {pid} could not be found "
                                 "in 'processors'")

        return selected_procs

    def _read_csv(self, req_qoi, filepath):
        return pd.read_csv(filepath, index_col=np.arange(req_qoi.nr_indices), header=[0])

    def _add_parid2idx(self, df, par_id):
        # from https://stackoverflow.com/questions/14744068/prepend-a-level-to-a-pandas-multiindex
        return pd.concat([df], keys=[par_id], names=["par_id"])

    def read_and_extract_qois(self, par_id, output_path):

        read_data = dict()

        for k in self.req_qois:
            filepath = os.path.join(output_path, k.filename)
            df_data = self._read_csv(k, filepath)
            read_data[k.filename] = self._add_parid2idx(df_data, par_id)    # filename is identifier for QoI

        return read_data

if __name__ == "__main__":
    a = QuantityOfInterest("evacuationTimes.txt", EnvironmentManager("corner"))

    print(a.req_qois)