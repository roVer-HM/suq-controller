#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import os
import subprocess
import pandas as pd
import numpy as np

from try_outs.utils.general import create_folder
from try_outs.qoi import QuantityOfInterest, EvacuationTime
from try_outs.environment import EnvironmentManager

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class Query(object):

    def __init__(self, env_manager: EnvironmentManager, qoi: QuantityOfInterest):
        self._env_man = env_manager
        self._qoi = qoi

    def query(self):
        # TODO: at the moment everything is simulated that is also previously generated via ParameterVariation
        var_scenarios = self._env_man.get_vadere_scenario_variations()

        # TODO: later this should be via par_id and time dependent
        results = pd.DataFrame(np.nan, index=np.arange(len(var_scenarios)), columns=[self._qoi.name])

        for pid, scfp in enumerate(var_scenarios):
            sc_name = os.path.basename(scfp).split(".scenario")[0]
            output_path = os.path.join(self._env_man.get_vadere_scenarios_folder(), "".join([sc_name, "_output"]))
            create_folder(output_path)
            self._simulate(scfp, output_path)
            results.iloc[pid, :] = self._qoi.read_and_extract_qoi(output_path)
        return results

    def _simulate(self, scenario_fp, output_path):
        model_path = self._env_man.get_model_path()
        subprocess.call(["java", "-jar", model_path, "suq", "-f", scenario_fp, "-o", output_path])


if __name__ == "__main__":
    em = EnvironmentManager.set_by_env_name("corner")
    r =  Query(em, EvacuationTime()).query()
    print(r)
