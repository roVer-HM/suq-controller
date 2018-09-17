#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import subprocess
import multiprocessing

import pandas as pd
import numpy as np

from suqc.qoi import QoIProcessor, PedestrianEvacuationTimeProcessor, AreaDensityVoronoiProcessor
from suqc.configuration import EnvironmentManager
from suqc.parameter import ParameterVariation, FullGridSampling, RandomSampling, BoxSampling
from suqc.resultformat import ResultDF

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class Query(object):

    def __init__(self, env_manager: EnvironmentManager, par_var: ParameterVariation, qoi: QoIProcessor):
        self._env_man = env_manager
        self._par_var = par_var
        self._result_df = ResultDF(self._par_var)
        self._qoi = qoi

    @property
    def result(self):
        return self._result_df.data

    def _simulate(self, scenario_fp, output_path):
        model_path = self._env_man.get_model_path()
        subprocess.call(["java", "-jar", model_path, "suq", "-f", scenario_fp, "-o", output_path])

    def _single_query(self, kwargs):
        output_path = self._env_man.get_output_path(kwargs["par_id"], create=True)
        self._simulate(kwargs["scenario_path"], output_path)
        result = self._qoi.read_and_extract_qoi(kwargs["par_id"], output_path)
        return result  # because of the multi-processor, don't try to already add the results here to _results_df

    @DeprecationWarning
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

        elif ty == pd.Series:  # series (usually time dependent)
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

    def _sp_query(self, query_list):
        # enumerate returns tuple(par_id, scenario filepath) see ParameterVariation.generate_vadere_scenarios and
        # ParameterVariation._vars_object()
        results = list()
        for arg in query_list:
            results.append(self._single_query(arg))
        self._result_df.add_multi_results(results)

    def _mp_query(self, query_list, njobs):
        pool = multiprocessing.Pool(processes=njobs)
        results = pool.map(self._single_query, query_list)
        self._result_df.add_multi_results(results)

    def run(self, njobs: int=-1):
        query_list = self._par_var.generate_vadere_scenarios()
        nr_simulations = self._par_var.nr_par_variations()

        if njobs == -1:
            njobs = min(multiprocessing.cpu_count(), nr_simulations)
            print(f"INFO: Using {njobs} processes.")

        if njobs == 1:
            self._sp_query(query_list=query_list)
        else:
            self._mp_query(query_list=query_list, njobs=njobs)
        return self.result


if __name__ == "__main__":

    em = EnvironmentManager("fp_operator")
    # pv = FullGridSampling(em)
    # pv.add_dict_grid({"speedDistributionStandardDeviation": [0.0, 0.1, 0.2, 0.3], "speedDistributionMean": [1.2, 1.3]})
    #
    q0 = PedestrianEvacuationTimeProcessor(em)
    #q1 = PedestrianDensityGaussianProcessor(em) # TODO: need to check if qoi-processor is available in basis file!


    pv = BoxSampling(em)
    pv.create_grid("speedDistributionStandardDeviation", 0, 0.5, 3, 3)

    q = Query(em, pv, q0).run(njobs=-1)
    print(q)

    # q = Query(em, pv, AreaDensityVoronoiProcessor(em)).run(njobs=1)
    # print(q)
