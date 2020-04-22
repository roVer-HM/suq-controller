#!/usr/bin/env python3

import os
import sys

from suqc.parameter.parameter import LatinHyperCubeSampling, Parameter, DependentParameter
from tutorial.imports import *

# This is just to make sure that the systems path is set up correctly, to have correct imports, it can be ignored:
sys.path.append(os.path.abspath("."))
sys.path.append(os.path.abspath(".."))


run_local = True

###############################################################################################################
# Usecase: Set yourself the parameters you want to change. Do this by defining a list of dictionaries with the
# corresponding parameter. Again, the Vadere output is deleted after all scenarios run.


if __name__ == "__main__":  # main required by Windows to run in parallel


    #create sampling for rover - needs to be outsourced into Marions repo
    # example omnet:  Parameter("*.station[0].mobility.initialX", unit="m", simulator="omnet", range=[200, 201])

    parameter = [
        Parameter("sources.[id==3001].distributionParameters", simulator="vadere", range=[1.25, 30], list=[1.25],
                  list_index=0)
       ]

    dependent_parameters = [
        
        DependentParameter(name="sources.[id==3002].distributionParameters", simulator="vadere",
                           equation=" = 1 * sources.[id==3001].distributionParameters ", list=[1.25], list_index=0),
        DependentParameter(name="sources.[id==3003].distributionParameters", simulator="vadere",
                           equation=" = 1 * sources.[id==3001].distributionParameters ", list=[1.25], list_index=0),
        DependentParameter(name="sources.[id==3004].distributionParameters", simulator="vadere",
                           equation=" = 1 * sources.[id==3001].distributionParameters ", list=[1.25], list_index=0)
    ]

    par_var = LatinHyperCubeSampling(parameters = parameter, parameters_dependent = dependent_parameters).get_sampling(2)

    path2ini = "/home/christina/repos/rover-main/rover/simulations/simple_detoure_suqc/omnetpp.ini"
    path2model = "Coupled"

    setup = CoupledDictVariation(
        ini_path=path2ini,
        scenario_name="simple_detour_100x177_miat1.25.scenario",
        parameter_dict_list=par_var,
        qoi="DegreeInformed.txt",
        model=path2model,
        scenario_runs=1,
        post_changes=PostScenarioChangesBase(apply_default=True),
        output_path=path2tutorial,
        output_folder="simple",
        remove_output=False,
    )

    if run_local:
        par_var, data = setup.run(
            1
        )  # -1 indicates to use all cores available to parallelize the scenarios
        # to do: allow -1 for rover containers
    else:
        par_var, data = setup.remote(-1)

    print("\n \n ---------------------------------------\n \n")
    print("ALL USED PARAMETER:")
    print(par_var)

    print("COLLECTED DATA:")
    print(data)
