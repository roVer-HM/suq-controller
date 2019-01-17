#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import abc
import os
from enum import Enum


import pandas as pd
import numpy as np


from suqc.utils.dict_utils import deep_dict_lookup

from suqc.utils.general import cast_series_if_possible
from suqc.configuration import EnvironmentManager
from suqc.resultformat import ParameterResult

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------

 # TODO: see also vadere issue #199, to include this information in the scenario

map_datakey2index = {
    "TimeStepKey": "timeStep",
    "TimeStepPedestrianIdOverlapKey": ["timeStep", "pedestrianId", "overlaüPedestrianId"],
    "TimestepPedestrianIdKey": ["timeStep", "pedestrianId"],
    "PedestrianIdKey": "pedestrianId",
    "IdDataKey": "id",
    "TimestepPositionKey": ["timeStep", "x", "y"],
    "TimestepRowKey": ["timeStep", "row"],
    "NoDataKey": None
}


class FileDataInfo(object):

    def __init__(self, process_file, processors):
        pass


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

        # TODO: collect processors involved to each file and get index

        pass

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

    def read_and_extract_qois(self):
        pass




if __name__ == "__main__":
    QuantityOfInterest("evacuationTimes.txt", EnvironmentManager("corner"))