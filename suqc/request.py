#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import multiprocessing
import hashlib
import os

import pandas as pd
import numpy as np

from suqc.qoi import QuantityOfInterest
from suqc.configuration import EnvironmentManager
from suqc.parameter.sampling import *
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

    def __init__(self, env_man: EnvironmentManager, par_var: ParameterVariation,
                 qoi: Union[str, List[str], QuantityOfInterest], sc_change: ScenarioChanges = None):

        self._env_man = env_man

        if isinstance(qoi, (str, list)):
            self._qoi = QuantityOfInterest(requested_files=qoi, em=self._env_man)
        else:  # type(qoi) == QuantityOfInterest
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
                filenames = list(ires.keys())
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
                    if ires is not None:
                        collected_data.append(ires[f])

                collected_data = pd.concat(collected_data, axis=0)
                final_results[f] = collected_data

        if len(filenames) == 1 and filenames is not None:
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


def QuickRequest(scenario_path: str, parameter_var: List[dict], qoi: Union[str, List[str]], model: str, njobs:int=1):
    """Removes all output again after it is collected from the Vadere output files. This method is best for interactive
    retuests."""

    assert os.path.exists(scenario_path) and scenario_path.endswith(".scenario"), \
        "Filepath must exist and the file has to end with .scenario"

    # results are only returned, not saved, but output has to be saved, the removed again.
    temporary_env_name = "_".join(["temporary", os.path.basename(scenario_path).replace(".scenario", ""),
                                   hashlib.sha1(scenario_path.encode()).hexdigest()])

    try:
        env = EnvironmentManager.create_environment(
            env_name=temporary_env_name, basis_scenario=scenario_path, model=model, replace=True)

        par_var = UserDefinedSampling(parameter_var)

        result_request = Request(env, par_var, qoi).run(njobs=njobs)
        return result_request

    finally:
        # clear up: the results are not saved for QuickRequests
        EnvironmentManager.remove_environment(name=temporary_env_name, force=True)


def SingleKeyRequest(scenario_path: str, key: str, values: np.ndarray, qoi: Union[str, List[str]],
                     model: str, njobs:int=1):
    simple_grid = [{key: v} for v in values]
    return QuickRequest(scenario_path, parameter_var=simple_grid, qoi=qoi, model=model, njobs=njobs)


if __name__ == "__main__":
    # par, res = QuickRequest(scenario_path="/home/daniel/REPOS/suq-controller/suqc/rimea_13_stairs_long_nelder_mead.scenario",
    #              parameter_var=[{"speedDistributionMean": 0.1}, {"speedDistributionMean": 0.2}, {"speedDistributionMean": 0.3}],
    #              qoi="postvis.trajectories", model="vadere0_7rc.jar")

    par, res = SingleKeyRequest(scenario_path="/home/daniel/REPOS/suq-controller/suqc/rimea_13_stairs_long_nelder_mead.scenario",
                                key="speedDistributionMean", values=np.array([0.1, 0.2, 0.3]),
                                qoi="postvis.trajectories",
                                model="vadere0_7rc.jar")


    print(res)

    exit()

    em = EnvironmentManager("corner", model="vadere0_7rc.jar")
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
