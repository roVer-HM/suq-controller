#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import subprocess
import multiprocessing

from suqc.qoi import QoIProcessor, PedestrianEvacuationTimeProcessor, AreaDensityVoronoiProcessor
from suqc.configuration import EnvironmentManager
from suqc.parameter.sampling import ParameterVariation, FullGridSampling, RandomSampling, BoxSampling
from suqc.parameter.postchanges import ScenarioChanges
from suqc.parameter.create import VadereScenarioCreation
from suqc.resultformat import ResultDF

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class Query(object):

    def __init__(self, env_man: EnvironmentManager, par_var: ParameterVariation, qoi: QoIProcessor,
                 sc_change: ScenarioChanges=None):

        self._env_man = env_man
        self._par_var = par_var
        self._qoi = qoi
        self._sc_change = sc_change

        self._result_df = ResultDF()
        self._result_df.add_par_var_data(self._par_var.points)

    @property
    def result(self):
        return self._result_df.data

    def _run_vadere_simulation(self, scenario_fp, output_path):
        model_path = self._env_man.get_model_path()
        subprocess.call(["java", "-jar", model_path, "suq", "-f", scenario_fp, "-o", output_path])

    def _single_query(self, kwargs):
        output_path = self._env_man.get_output_path(kwargs["par_id"], create=True)
        self._run_vadere_simulation(kwargs["scenario_path"], output_path)
        result = self._qoi.read_and_extract_qoi(kwargs["par_id"], output_path)
        return result  # because of the multi-processor, don't try to already add the results here to _results_df

    def _sp_query(self, query_list):
        # enumerate returns tuple(par_id, scenario filepath) see ParameterVariation.generate_vadere_scenarios and
        # ParameterVariation._vars_object()
        results = list()
        for arg in query_list:
            results.append(self._single_query(arg))
        self._result_df.add_qoi_data(results)

    def _mp_query(self, query_list, njobs):
        pool = multiprocessing.Pool(processes=njobs)
        results = pool.map(self._single_query, query_list)
        self._result_df.add_qoi_data(results)

    def run(self, njobs: int=-1):

        vadcreate = VadereScenarioCreation(self._env_man, self._par_var, self._sc_change)
        query_list = vadcreate.generate_vadere_scenarios()

        nr_simulations = self._par_var.nr_par_variations()

        if njobs == -1:
            avail_cpus = multiprocessing.cpu_count()
            njobs = min(avail_cpus, nr_simulations)
            print(f"INFO: Available cpus: {avail_cpus}. Nr. of simulation {nr_simulations}. Setting to {njobs} processes.")

        if njobs == 1:
            self._sp_query(query_list=query_list)
        else:
            self._mp_query(query_list=query_list, njobs=njobs)
        return self.result


if __name__ == "__main__":

    em = EnvironmentManager("corner")
    # pv = FullGridSampling(em)
    # pv.add_dict_grid({"speedDistributionStandardDeviation": [0.0, 0.1, 0.2, 0.3], "speedDistributionMean": [1.2, 1.3]})
    #
    q0 = PedestrianEvacuationTimeProcessor(em)
    #q1 = PedestrianDensityGaussianProcessor(em) # TODO: need to check if qoi-processor is available in basis file!


    pv = BoxSampling()
    pv.create_grid("speedDistributionStandardDeviation", 0, 0.5, 3, 3)

    sc = ScenarioChanges(apply_default=True)

    q = Query(em, pv, q0, sc).run(njobs=-1)
    print(q)

    # q = Query(em, pv, AreaDensityVoronoiProcessor(em)).run(njobs=1)
    # print(q)
