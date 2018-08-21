#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import os
import subprocess
import multiprocessing

import pandas as pd
import numpy as np

from try_outs.utils.general import create_folder
from try_outs.qoi import QuantityOfInterest, EvacuationTime
from try_outs.environment import EnvironmentManager
from try_outs.parameter import ParameterVariation

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

    def _simulate(self, scenario_fp, output_path):
        model_path = self._env_man.get_model_path()
        subprocess.call(["java", "-jar", model_path, "suq", "-f", scenario_fp, "-o", output_path])

    def _single_query(self, arg):
        pid = arg[0]
        scfp = arg[1]

        sc_name = os.path.basename(scfp).split(".scenario")[0]
        output_path = os.path.join(self._env_man.path_scenario_variation_folder(), "".join([sc_name, "_output"]))
        create_folder(output_path)
        self._simulate(scfp, output_path)
        return pid, self._qoi.read_and_extract_qoi(output_path)

    def _create_and_fill_df(self, list_results):
        # TODO: later this should also support time dependent qoi!
        idx = pd.Index(np.arange(len(list_results)), name="par_id")
        results = pd.DataFrame(np.nan, index=idx, columns=[self._qoi.name])
        for pid, res in list_results:
            results.loc[pid, :] = res
        return results

    def _mp_query(self, njobs, var_scenarios):
        pool = multiprocessing.Pool(processes=njobs)
        res = pool.map(self._single_query, enumerate(var_scenarios))
        return self._create_and_fill_df(res)

    def _sp_query(self, var_scenarios):
        res = list()

        # TODO: the par_id probably matches the real case, but the file lookup table should be used!
        for qu in enumerate(var_scenarios):  # enumerate returns tuple(par_id, scenario filepath)
            res.append(self._single_query(qu))
        return self._create_and_fill_df(res)

    def query_simulate_all_new(self, par_var: ParameterVariation, njobs=-1):
        # simulate all means all is simulated (no check in storage), 'new' means all previous outputs are removed
        par_var.generate_store_scenario_variation_files()
        return self.query(njobs)

    def query(self, njobs=-1):
        # TODO: at the moment everything is simulated that is also previously generated via ParameterVariation
        var_scenarios = self._env_man.get_vadere_scenario_variations()
        if njobs == -1:
           njobs = min(multiprocessing.cpu_count(), len(var_scenarios))

        if njobs == 1:
            df_query = self._sp_query(var_scenarios)
        else:
            df_query = self._mp_query(njobs, var_scenarios)
        return df_query


if __name__ == "__main__":
    em = EnvironmentManager.set_by_env_name("corner")
    pv = ParameterVariation(em)
    pv.add_dict_grid({"speedDistributionStandardDeviation": [0.0, 0.1, 0.2, 0.3]})
    r = Query(em, EvacuationTime()).query_simulate_all_new(pv)
    print(r)
