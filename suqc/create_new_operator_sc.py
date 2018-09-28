#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import suqc.configuration as suqcfg


from suqc.configuration import EnvironmentManager
from suqc.qoi import InitialAndLastPositionProcessor, PedestrianEvacuationTimeProcessor
from suqc.query import Query
from suqc.parameter.sampling import FullGridSampling

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


if False:
    suqcfg.create_environment_from_file(
        name="new_operator_scenario",
        filepath="./../scenario_basis_fp_operator.scenario",
        model="vadere",
        replace=True)


env_man = EnvironmentManager(name="new_operator_scenario")

par = FullGridSampling()
par.add_dict_grid({"speedDistributionMean": [0.6, 0.7, 0.8]})

qoi = InitialAndLastPositionProcessor(env_man)

#qoi = PedestrianEvacuationTimeProcessor(env_man)

result, par = Query(env_man=env_man, par_var=par, qoi=qoi).run(njobs=1)

print(result)

