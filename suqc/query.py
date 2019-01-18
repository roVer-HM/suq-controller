#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import subprocess
import multiprocessing

import pandas as pd

from suqc.qoi import QuantityOfInterest
from suqc.configuration import EnvironmentManager
from suqc.parameter.sampling import ParameterVariation, FullGridSampling, RandomSampling, BoxSamplingUlamMethod
from suqc.parameter.postchanges import ScenarioChanges
from suqc.parameter.create import VadereScenarioCreation

from typing import List

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class Query(object):

    def __init__(self, env_man: EnvironmentManager, par_var: ParameterVariation, qoi: QuantityOfInterest,
                 sc_change: ScenarioChanges=None):
        self._env_man = env_man
        self._qoi = qoi
        self._sc_change = sc_change

        self.par_var = par_var
        self.result = None

    def _run_vadere_simulation(self, scenario_fp, output_path):
        model_path = self._env_man.get_model_path()
        return subprocess.call(["java", "-jar", model_path, "suq", "-f", scenario_fp, "-o", output_path])

    def _interpret_return_value(self, ret_val, par_id):
        if ret_val == 0:
            return True
        elif ret_val == 1:
            print(f"WARNING: Simulation with parameter setting {par_id} failed.")
            return False

    def _single_query(self, kwargs):
        par_id = kwargs["par_id"]

        output_path = self._env_man.get_output_path(par_id, create=True)
        ret_val = self._run_vadere_simulation(kwargs["scenario_path"], output_path)
        is_results = self._interpret_return_value(ret_val, par_id)

        if is_results:
            result = self._qoi.read_and_extract_qois(par_id, output_path)
        else:
            result = None

        return result  # because of the multi-processor, don't try to already add the results here to _results_df

    def _finalize_results(self, results: List[dict]):

        filenames = None
        for ires in results:
            if ires is not None:
                # it is assumed that the the keys for all elements in results are the same!
                filenames = results[0].keys()

        if filenames is None:
            print("WARNING: All simulations failed, only 'None' results.")
            final_results = None
        else:

            final_results = dict()

            for f in filenames:

                collected_data = list()

                for ires in results:
                    collected_data.append(ires[f])

                collected_data = pd.concat(collected_data, axis=0)
                final_results[f] = collected_data

        return final_results

    def _sp_query(self, query_list):
        # enumerate returns tuple(par_id, scenario filepath) see ParameterVariation.generate_vadere_scenarios and
        # ParameterVariation._vars_object()
        results = list()
        for arg in query_list:
            results.append(self._single_query(arg))

        self.result = self._finalize_results(results)

    def _mp_query(self, query_list, njobs):
        pool = multiprocessing.Pool(processes=njobs)
        results = pool.map(self._single_query, query_list)
        self.result = self._finalize_results(results)

    def run(self, njobs: int=-1):

        assert njobs != 0 or njobs < -1, "njobs cannot be zero or smaller than -1"

        nr_simulations = self.par_var.points.shape[0]  # nr of rows = nr of parameter settings = #simulations

        if njobs == -1:
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


if __name__ == "__main__":

    em = EnvironmentManager("corner")
    pv = FullGridSampling()
    pv.add_dict_grid({"speedDistributionStandardDeviation": [0.0, 0.1, 0.2, 0.3], "speedDistributionMean": [1.2, 1.3]})
    q0 = QuantityOfInterest("evacuationTimes.txt", em)

    q = Query(em, pv, q0).run(njobs=1)

    print(q)


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
