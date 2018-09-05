#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import os
import subprocess
import multiprocessing
import copy

import pandas as pd
import numpy as np

from qoi import QoIProcessor, PedestrianEvacuationTimeProcessor, AreaDensityVoronoiProcessor
from configuration import EnvironmentManager
from parameter import ParameterVariation

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class Query(object):

    def __init__(self, env_manager: EnvironmentManager, qoi: QoIProcessor):
        self._env_man = env_manager
        self._qoi = qoi

    def _simulate(self, scenario_fp, output_path):
        model_path = self._env_man.get_model_path()
        subprocess.call(["java", "-jar", model_path, "suq", "-f", scenario_fp, "-o", output_path])

    def _args_query_request(self, **kwargs):

        var_scenarios = self._env_man.get_vadere_scenario_variations()

        ret_list = list()
        def_dict = {"par_id": None, "scenario_path": None, "kwargs_qoi": None}

        for pid, path in var_scenarios:
            d = copy.deepcopy(def_dict)
            d["par_id"] = pid
            d["scenario_path"] = path
            d["kwargs_qoi"] = kwargs
            ret_list.append(d)
        return ret_list

    def _single_query(self, kwargs):
        pid = kwargs["par_id"]
        scfp = kwargs["scenario_path"]
        kwargs_qoi = kwargs["kwargs_qoi"]  # all arguments handled to the QoI processor

        sc_name = os.path.basename(scfp).split(".scenario")[0]  # TODO: do this better, possibly via env.manager
        output_path = self._env_man.get_output_path(sc_name, create=True)

        self._simulate(scfp, output_path)
        return pid, self._qoi.read_and_extract_qoi(output_path, **kwargs_qoi)

    def _create_and_fill_df(self, list_results):

        assert len(set([type(i[1]) for i in list_results])) == 1, "Only list of equal return type of QoI supported!"

        test_element = list_results[0][1]
        ty = type(test_element)

        if ty == float:  # scalars (non time dependenent)
            idx = pd.Index([i[0] for i in list_results], name="par_id")
            col = pd.Index([self._qoi.name], name="qoi")

            results = pd.DataFrame(np.nan, index=idx, columns=col)
            for pid, res in list_results:
                results.loc[pid, :] = res

        elif ty == pd.Series:  # series (usually time dependenent)
            # change 'name' and 'index' of series to concat it into a DF:
            for pid, series in list_results:
                series.name = str(pid)

                # The Series read gets a MultiIndex with upper level = QoI name and lower the name read from the output
                # which is mostly time...
                series.index = pd.MultiIndex.from_product([[self._qoi.name], series.index],
                                                          names=["qoi", series.index.name])
            results = pd.concat([i[1] for i in list_results], axis=1).T
            results.index.name = "par_id"
        else:
            raise RuntimeError("Type not supported!")

        return results

    def _mp_query(self, njobs, **kwargs):
        pool = multiprocessing.Pool(processes=njobs)
        res = pool.map(self._single_query, self._args_query_request(**kwargs))
        return self._create_and_fill_df(res)

    def _sp_query(self, **kwargs):
        res = list()

        # TODO: the par_id probably matches the real case, but the file lookup table should be used!
        for arg in self._args_query_request(**kwargs):  # enumerate returns tuple(par_id, scenario filepath)
            res.append(self._single_query(arg))
        return self._create_and_fill_df(res)

    def query_simulate_all_new(self, par_var: ParameterVariation, njobs: int=-1):
        # simulate all means all is simulated (no check in storage), 'new' means all previous outputs are removed
        par_var.generate_store_scenario_variation_files()
        return self.query_existing(njobs)

    def query_existing(self, njobs: int=-1):
        nr_simulations = self._env_man.get_nr_variations()

        if njobs == -1:
           njobs = min(multiprocessing.cpu_count(), nr_simulations)

        if njobs == 1:
            df_query = self._sp_query()
        else:
            df_query = self._mp_query(njobs)
        return df_query


if __name__ == "__main__":
    em = EnvironmentManager.set_by_env_name("corner")
    pv = ParameterVariation(em)
    pv.add_dict_grid({"speedDistributionStandardDeviation": [0.0, 0.1, 0.2, 0.3]})
    r = Query(em, PedestrianEvacuationTimeProcessor(em)).query_simulate_all_new(pv, njobs=1)
    r = Query(em, AreaDensityVoronoiProcessor(em)).query_simulate_all_new(pv, njobs=-1)
    print(r)
