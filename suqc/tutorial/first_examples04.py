#!/usr/bin/env python3 

from suqc.tutorial.imports import *


# TODO: not yet ready!
run_local = True

###############################################################################################################
# Usecase: Most functionality to define a grid.

env_man = EnvironmentManager.create_environment("test_remote",
                                                basis_scenario="/home/daniel/REPOS/vadere/VadereModelTests/TestOSM/scenarios/basic_2_density_discrete_ca.scenario",
                                                replace=True)

par_var = FullGridSampling(grid={"speedDistributionMean": np.array([1., 1.2])})

setup = FullVaryScenario(env_man=env_man, par_var=par_var, qoi="density.txt", model="vadere0_7rc.jar", njobs=1)


if run_local:
    par_lookup, data = setup.run(2)
else:
    par_lookup, data = setup.remote(2)

print(par_lookup)
print(data)