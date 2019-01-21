#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import multiprocessing

import pandas as pd
import numpy as np

import os

from suqc.qoi import QuantityOfInterest
from suqc.configuration import EnvironmentManager
from suqc.parameter.sampling import ParameterVariation, FullGridSampling, RandomSampling, BoxSamplingUlamMethod
from suqc.parameter.postchanges import ScenarioChanges
from suqc.parameter.create import VadereScenarioCreation

from typing import *

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class Request(object):

    def __init__(self, env_man: EnvironmentManager, par_var: ParameterVariation, qoi: QuantityOfInterest,
                 sc_change: ScenarioChanges=None):
        self._env_man = env_man
        self._qoi = qoi
        self._sc_change = sc_change

        self.par_var = par_var
        self._add_required_time_column()

        self.result = None

    def _add_required_time_column(self):
        self.par_var.points.loc[:, "req_time"] = np.nan

    def _interpret_return_value(self, ret_val, par_id):
        if ret_val == 0:
            return True
        elif ret_val == 1:
            print(f"WARNING: Simulation with parameter setting {par_id} failed.")
            return False

    def _single_query(self, kwargs) -> Tuple[dict, np.float64]:
        par_id = kwargs["par_id"]

        output_path = self._env_man.get_par_id_output_path(par_id, create=True)
        ret_val, req_time = self._env_man.model.run_simulation(kwargs["scenario_path"], output_path)
        is_results = self._interpret_return_value(ret_val, par_id)

        if is_results:
            result = self._qoi.read_and_extract_qois(par_id, output_path)
        else:
            result = None
            req_time = np.nan

        # because of the multi-processor, don't try to already add the results here to _results_df
        return result, req_time

    def _finalize_results(self, results: List[dict]):

        filenames = None
        for ires in results:
            if ires is not None:
                # it is assumed that the the keys for all elements in results are the same!
                filenames = list(results[0].keys())
                break

        if filenames is None:
            print("WARNING: All simulations failed, only 'None' results.")
            final_results = None
        else:
            # Successful runs are collected and are concatenated into a single pd.DataFrame below
            final_results = dict()

            for f in filenames:

                collected_data = list()

                for ires in results:
                    collected_data.append(ires[f])

                collected_data = pd.concat(collected_data, axis=0)
                final_results[f] = collected_data

        if len(filenames) == 1:
            # there is no need to have the key/value if only file was requested
            final_results = final_results[filenames[0]]

        return final_results

    def _sp_query(self, query_list):
        # enumerate returns tuple(par_id, scenario filepath) see ParameterVariation.generate_vadere_scenarios and
        # ParameterVariation._vars_object()
        results = list()
        for arg in query_list:
            res, req_time = self._single_query(arg)
            results.append(res)
            self.par_var.points.loc[arg["par_id"], "req_time"] = req_time

        self.result = self._finalize_results(results)

    def _mp_query(self, query_list, njobs):
        pool = multiprocessing.Pool(processes=njobs)
        all_results = pool.map(self._single_query, query_list)

        data_results, req_times = list(zip(*all_results))

        idx = [q["par_id"] for q in query_list]

        self.par_var.points.loc[idx, "req_times"] = req_times
        self.result = self._finalize_results(data_results)

    def run(self, njobs: int = -1):

        assert not isinstance(njobs, int) or njobs != 0 or njobs < -1, \
            "njobs has to be an integer and cannot be zero or smaller than -1"

        nr_simulations = self.par_var.points.shape[0]  # nr of rows = nr of parameter settings = #simulations

        if njobs == -1:  # this is adapted to scikit-learn way
            avail_cpus = multiprocessing.cpu_count()
            njobs = min(avail_cpus, nr_simulations)
            print(f"INFO: Available cpus: {avail_cpus}. Nr. of simulation {nr_simulations}. "
                  f"Setting to {njobs} processes.")

        vadcreate = VadereScenarioCreation(self._env_man, self.par_var, self._sc_change)
        query_list = vadcreate.generate_vadere_scenarios(njobs)

        if njobs == 1:
            self._sp_query(query_list=query_list)
        else:
            self._mp_query(query_list=query_list, njobs=njobs)
        return self.par_var.points, self.result


class QuickRequest(object):

    def __init__(self, scenario_path: str, parameter_var: List[dict], qoi: List[str], model: str):

        assert os.path.exists(scenario_path) and scenario_path.endswith(".scenario"), \
            "Filepath must exist and the file has to end with .scenario"
        import hashlib

        # results are only returned, not saved, but output has to be saved, the removed again.
        temporary_env_name = os.path.basename(scenario_path) + hashlib.sha1(scenario_path)


        env = EnvironmentManager.create_environment(
            env_name=temporary_env_name, basis_scenario=scenario_path, model=model, replace=False)

        par_var = ParameterVariation.individual()

        # TODO: provide an user specified way, not all parameters have to be changed all the time.
        self._par_var = ParameterVariation(parameter_var)

        QuantityOfInterest(qoi, self._em)


class SingleKeyRequest(object):

    def __init__(self, scenario_path: str, key: str, values: np.ndarray):
        # Idea: only for one key, which is probably one of the most often required
        # Return only a single DataFrame, join parameter lookup and results
        # TODO
        pass


if __name__ == "__main__":

    em = EnvironmentManager("corner", model="vadere0_6.jar")
    pv = FullGridSampling()
    pv.add_dict_grid({"speedDistributionStandardDeviation": [0.0, 0.1, 0.2, 0.3], "speedDistributionMean": [1.2, 1.3]})
    q0 = QuantityOfInterest("evacuationTimes.txt", em)

    par_lu, result = Request(em, pv, q0).run(njobs=1)

    exit()

    #q1 = PedestrianDensityGaussianProcessor(em) # TODO: need to check if qoi-processor is available in basis file!
    #
    #
    # pv = BoxSamplingUlamMethod()
    # pv.create_grid("speedDistributionStandardDeviation", 0, 0.5, 3, 3)
    #
    # sc = ScenarioChanges(apply_default=True)
    #
    # q = Query(em, pv, q0, sc).run(njobs=-1)
    # print(q)
    #
    # # q = Query(em, pv, AreaDensityVoronoiProcessor(em)).run(njobs=1)
    # # print(q)
