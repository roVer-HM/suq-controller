#!/usr/bin/env python3
#!/usr/bin/python3

import sys
import random

from suqc.parameter.sampling import (
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


def test_me():

    # define roVer simulation
    path2ini = os.path.join(
        os.environ["ROVER_MAIN"], "rover/simulations/simple_detoure_suqc/omnetpp.ini"
    )  # use this ini-file

    output_folder = os.path.join(path2tutorial, sys._getframe().f_code.co_name,)

    qoi = [
        "degree_informed_extract.txt",
        "poisson_parameter.txt",
        "time_95_informed.txt",
    ]  # qoi

    parameter = [
        Parameter(name="number_of_agents_mean", simulator="dummy", stages=[0.2, 0.3],)
    ]
    dependent_parameters = [
        DependentParameter(
            name="sources.[id==5].distributionParameters",
            simulator="vadere",
            equation=lambda args: [(args["number_of_agents_mean"])],
        ),
        DependentParameter(name="sim-time-limit", simulator="omnet", equation="180s"),
        DependentParameter(
            name="*.station[0].app[0].incidentTime", simulator="omnet", equation="100s",
        ),
        DependentParameter(
            name="*.radioMedium.obstacleLoss.typename",
            simulator="omnet",
            equation="DielectricObstacleLoss",
        ),
        # DependentParameter(
        #     name="*.manager.useVadereSeed", simulator="omnet", equation="false",
        # ),
        # DependentParameter(
        #     name="*.manager.seed",
        #     simulator="omnet",
        #     equation=lambda x: str(random.randint(2, 9)),
        # ),
    ]

    reps = [3, 1, 20]
    par_var = RoverSamplingFullFactorial(
        parameters=parameter, parameters_dependent=dependent_parameters
    ).get_sampling()

    setup = CoupledDictVariation(
        ini_path=path2ini,
        config="final",
        parameter_dict_list=par_var,
        qoi=qoi,
        model="Coupled",
        scenario_runs=reps,
        post_changes=PostScenarioChangesBase(apply_default=True),
        output_path=path2tutorial,
        output_folder=output_folder,
        remove_output=True,
        seed_config={"vadere": "fixed", "omnet": "random"},
        env_remote=None,
    )

    if run_local:
        par_var, data = setup.run(4)
    else:
        par_var, data = setup.remote(-1)

    summary = output_folder

    par_var.to_pickle(os.path.join(summary, "metainfo.pkl"))

    data["poisson_parameter.txt"].to_pickle(
        os.path.join(summary, "poisson_parameter.pkl")
    )
    data["degree_informed_extract.txt"].to_pickle(
        os.path.join(summary, "degree_informed_extract.pkl")
    )
    data["time_95_informed.txt"].to_pickle(
        os.path.join(summary, "time_95_informed.pkl")
    )

    print("Simulation study finished.")


if __name__ == "__main__":

    if os.environ["ROVER_MAIN"] is None:
        print("Please provide ROVER_MAIN system variable.")
    test_me()
