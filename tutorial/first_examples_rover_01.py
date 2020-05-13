#!/usr/bin/env python3
#!/usr/bin/python3

import sys

from suqc.parameter.parameter import (
    DependentParameter,
    Parameter,
    RoverSamplingFullFactorial,
)
from tutorial.imports import *

# This is just to make sure that the systems path is set up correctly, to have correct imports, it can be ignored:
sys.path.append(os.path.abspath("."))
sys.path.append(os.path.abspath(".."))

run_local = True
###############################################################################################################
# Usecase: Set yourself the parameters you want to change. Do this by defining a list of dictionaries with the
# corresponding parameter. Again, the Vadere output is deleted after all scenarios run.


def preprocessing_and_simulation_run(
    par_var, path2ini, output_folder, qoi, repitions=1
):

    path2model = "Coupled"

    setup = CoupledDictVariation(
        ini_path=path2ini,
        scenario_name="simple_detour_100x177_miat1.25.scenario",
        parameter_dict_list=par_var,
        qoi=qoi,
        model=path2model,
        scenario_runs=repitions,
        post_changes=PostScenarioChangesBase(apply_default=True),
        output_path=path2tutorial,
        output_folder=output_folder,
        remove_output=False,
        remove_omnet_files=True,
    )

    if run_local:
        par_var, data = setup.run(
            1
        )  # -1 indicates to use all cores available to parallelize the scenarios
        # to do: allow -1 for rover containers
    else:
        par_var, data = setup.remote(-1)

    print("simulation runs: finished")


def fp_traffic_no__obstacle_yes__seed_none():

    # define roVer simulation
    path2ini = os.path.join(
        os.environ["ROVER_MAIN"], "rover/simulations/simple_detoure_suqc/omnetpp.ini"
    )  # use this ini-file

    output_folder = os.path.join(path2tutorial, sys._getframe().f_code.co_name,)
    qoi = "DegreeInformed.txt"  # qoi

    # create sampling for rover - needs to be outsourced into Marions repo
    # example omnet:  Parameter("*.station[0].mobility.initialX", unit="m", simulator="omnet", range=[200, 201])
    parameter = [
        Parameter(
            name="number_of_agents_mean",
            simulator="dummy",
            range=np.log10([25, 4000]).tolist(),
            stages=10,
        )
    ]

    dependent_parameters = [
        DependentParameter(
            name="sources.[id==3001].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3002].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3003].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)] ",
        ),
        DependentParameter(
            name="sources.[id==3004].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sim-time-limit", simulator="omnet", equation='= "180s"'
        ),
        DependentParameter(
            name="*.station[0].app[0].incidentTime",
            simulator="omnet",
            equation='= "100s"',
        ),
        DependentParameter(
            name="*.radioMedium.obstacleLoss.typename",
            simulator="omnet",
            equation='= "IdealObstacleLoss"',
        ),
        DependentParameter(
            name="*.manager.useVadereSeed", simulator="omnet", equation='= "true"',
        ),
    ]

    reps = [100, 100, 75, 75, 50, 50, 25, 25, 10, 10]
    par_var = RoverSamplingFullFactorial(
        parameters=parameter, parameters_dependent=dependent_parameters
    ).get_sampling()
    preprocessing_and_simulation_run(
        par_var, path2ini, output_folder, qoi, repitions=reps
    )


def fp_traffic_no__obstacle_yes__seed_set():

    # define roVer simulation
    path2ini = os.path.join(
        os.environ["ROVER_MAIN"], "rover/simulations/simple_detoure_suqc/omnetpp.ini"
    )  # use this ini-file

    output_folder = os.path.join(path2tutorial, sys._getframe().f_code.co_name,)

    qoi = "DegreeInformed.txt"  # qoi

    # create sampling for rover - needs to be outsourced into Marions repo
    # example omnet:  Parameter("*.station[0].mobility.initialX", unit="m", simulator="omnet", range=[200, 201])
    parameter = [
        Parameter(
            name="number_of_agents_mean",
            simulator="dummy",
            range=np.log10([25, 4000]).tolist(),
            stages=10,
        )
    ]

    dependent_parameters = [
        DependentParameter(
            name="sources.[id==3001].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3002].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3003].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)] ",
        ),
        DependentParameter(
            name="sources.[id==3004].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sim-time-limit", simulator="omnet", equation='= "180s"'
        ),
        DependentParameter(
            name="*.station[0].app[0].incidentTime",
            simulator="omnet",
            equation='= "100s"',
        ),
        DependentParameter(
            name="*.radioMedium.obstacleLoss.typename",
            simulator="omnet",
            equation='= "IdealObstacleLoss"',
        ),
        DependentParameter(
            name="*.manager.useVadereSeed", simulator="omnet", equation='= "false"',
        ),
    ]

    reps = 1
    par_var = RoverSamplingFullFactorial(
        parameters=parameter, parameters_dependent=dependent_parameters
    ).get_sampling()
    preprocessing_and_simulation_run(
        par_var, path2ini, output_folder, qoi, repitions=reps
    )


def fp_traffic_no__obstacle_no__seed_set():

    # define roVer simulation
    path2ini = os.path.join(
        os.environ["ROVER_MAIN"], "rover/simulations/simple_detoure_suqc/omnetpp.ini"
    )  # use this ini-file

    output_folder = os.path.join(path2tutorial, sys._getframe().f_code.co_name,)

    qoi = "DegreeInformed.txt"  # qoi

    # create sampling for rover - needs to be outsourced into Marions repo
    # example omnet:  Parameter("*.station[0].mobility.initialX", unit="m", simulator="omnet", range=[200, 201])
    parameter = [
        Parameter(
            name="number_of_agents_mean",
            simulator="dummy",
            range=np.log10([25, 4000]).tolist(),
            stages=10,
        )
    ]

    dependent_parameters = [
        DependentParameter(
            name="sources.[id==3001].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3002].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3003].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)] ",
        ),
        DependentParameter(
            name="sources.[id==3004].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sim-time-limit", simulator="omnet", equation='= "180s"'
        ),
        DependentParameter(
            name="*.station[0].app[0].incidentTime",
            simulator="omnet",
            equation='= "100s"',
        ),
        DependentParameter(
            name="*.radioMedium.obstacleLoss.typename",
            simulator="omnet",
            equation='= ""',
        ),
        DependentParameter(
            name="*.manager.useVadereSeed", simulator="omnet", equation='= "false"',
        ),
    ]

    reps = 1
    par_var = RoverSamplingFullFactorial(
        parameters=parameter, parameters_dependent=dependent_parameters
    ).get_sampling()
    preprocessing_and_simulation_run(
        par_var, path2ini, output_folder, qoi, repitions=reps
    )


def fp_traffic_yes__obstacle_yes__seed_set():

    # define roVer simulation
    # define roVer simulation
    path2ini = os.path.join(
        os.environ["ROVER_MAIN"],
        "rover/simulations/simple_detoure_suqc_traffic/omnetpp.ini",
    )  # use this ini-file

    output_folder = os.path.join(path2tutorial, sys._getframe().f_code.co_name,)
    qoi = "DegreeInformed.txt"  # qoi

    # create sampling for rover - needs to be outsourced into Marions repo
    # example omnet:  Parameter("*.station[0].mobility.initialX", unit="m", simulator="omnet", range=[200, 201])
    parameter = [
        Parameter(
            name="number_of_agents_mean",
            simulator="dummy",
            range=np.log10([25, 4000]).tolist(),
            stages=10,
        ),
        Parameter(
            name="*.hostMobile[*].app[1].messageLength",
            simulator="omnet",
            unit="B",
            stages=[500, 5000, 50000],
        ),
    ]

    dependent_parameters = [
        DependentParameter(
            name="sources.[id==3001].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3002].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3003].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)] ",
        ),
        DependentParameter(
            name="sources.[id==3004].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sim-time-limit", simulator="omnet", equation='= "180s"'
        ),
        DependentParameter(
            name="*.station[0].app[0].incidentTime",
            simulator="omnet",
            equation='= "100s"',
        ),
        DependentParameter(
            name="*.radioMedium.obstacleLoss.typename",
            simulator="omnet",
            equation='= "IdealObstacleLoss"',
        ),
        DependentParameter(
            name="*.manager.useVadereSeed", simulator="omnet", equation='= "false"',
        ),
    ]

    reps = 1
    par_var = RoverSamplingFullFactorial(
        parameters=parameter, parameters_dependent=dependent_parameters
    ).get_sampling()
    preprocessing_and_simulation_run(
        par_var, path2ini, output_folder, qoi, repitions=reps
    )


def fp_traffic_yes__obstacle_no__seed_set():

    # define roVer simulation
    # define roVer simulation
    path2ini = os.path.join(
        os.environ["ROVER_MAIN"],
        "rover/simulations/simple_detoure_suqc_traffic/omnetpp.ini",
    )  # use this ini-file

    output_folder = os.path.join(path2tutorial, sys._getframe().f_code.co_name,)
    qoi = "DegreeInformed.txt"  # qoi

    # create sampling for rover - needs to be outsourced into Marions repo
    # example omnet:  Parameter("*.station[0].mobility.initialX", unit="m", simulator="omnet", range=[200, 201])
    parameter = [
        Parameter(
            name="number_of_agents_mean",
            simulator="dummy",
            range=np.log10([25, 4000]).tolist(),
            stages=10,
        ),
        Parameter(
            name="*.hostMobile[*].app[1].messageLength",
            simulator="omnet",
            unit="B",
            stages=[500, 5000, 50000],
        ),
    ]

    dependent_parameters = [
        DependentParameter(
            name="sources.[id==3001].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3002].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3003].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)] ",
        ),
        DependentParameter(
            name="sources.[id==3004].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sim-time-limit", simulator="omnet", equation='= "180s"'
        ),
        DependentParameter(
            name="*.station[0].app[0].incidentTime",
            simulator="omnet",
            equation='= "100s"',
        ),
        DependentParameter(
            name="*.radioMedium.obstacleLoss.typename",
            simulator="omnet",
            equation='= ""',
        ),
        DependentParameter(
            name="*.manager.useVadereSeed", simulator="omnet", equation='= "false"',
        ),
    ]

    reps = 1
    par_var = RoverSamplingFullFactorial(
        parameters=parameter, parameters_dependent=dependent_parameters
    ).get_sampling()
    preprocessing_and_simulation_run(
        par_var, path2ini, output_folder, qoi, repitions=reps
    )


def test_me():

    # define roVer simulation
    path2ini = os.path.join(
        os.environ["ROVER_MAIN"], "rover/simulations/simple_detoure_suqc/omnetpp.ini"
    )  # use this ini-file

    output_folder = os.path.join(path2tutorial, sys._getframe().f_code.co_name,)

    qoi = "DegreeInformed.txt"  # qoi

    # create sampling for rover - needs to be outsourced into Marions repo
    # example omnet:  Parameter("*.station[0].mobility.initialX", unit="m", simulator="omnet", range=[200, 201])
    parameter = [
        Parameter(name="number_of_agents_mean", simulator="dummy", stages=[30, 30.5],)
    ]

    # equation=lambda args: [570 / args["number_of_agents_mean"]],

    dependent_parameters = [
        DependentParameter(
            name="sources.[id==3001].distributionParameters",
            simulator="vadere",
            equation=lambda args: [1000 / (args["number_of_agents_mean"])],
        ),
        DependentParameter(
            name="sources.[id==3002].distributionParameters",
            simulator="vadere",
            equation=lambda args: [1000 / (args["number_of_agents_mean"])],
        ),
        DependentParameter(
            name="sources.[id==3003].distributionParameters",
            simulator="vadere",
            equation=lambda args: [1000 / (args["number_of_agents_mean"])],
        ),
        DependentParameter(
            name="sources.[id==3004].distributionParameters",
            simulator="vadere",
            equation=lambda args: [1000 / (args["number_of_agents_mean"])],
        ),
        DependentParameter(name="sim-time-limit", simulator="omnet", equation="180s"),
        DependentParameter(
            name="*.station[0].app[0].incidentTime", simulator="omnet", equation="100s",
        ),
        DependentParameter(
            name="*.radioMedium.obstacleLoss.typename",
            simulator="omnet",
            equation="IdealObstacleLoss",
        ),
        DependentParameter(
            name="*.manager.useVadereSeed", simulator="omnet", equation="false",
        ),
    ]

    reps = 1
    par_var = RoverSamplingFullFactorial(
        parameters=parameter, parameters_dependent=dependent_parameters
    ).get_sampling()
    preprocessing_and_simulation_run(
        par_var, path2ini, output_folder, qoi, repitions=reps
    )


if __name__ == "__main__":

    # os.environ["ROVER_MAIN"] = "/home/christina/repos/rover-main"
    test_me()

    # fp_traffic_no__obstacle_no__seed_set()
    # fp_traffic_no__obstacle_yes__seed_none()
    # fp_traffic_no__obstacle_yes__seed_set()
    # fp_traffic_yes__obstacle_no__seed_set()
    # fp_traffic_yes__obstacle_yes__seed_set()
