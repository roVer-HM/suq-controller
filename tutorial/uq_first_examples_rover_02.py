#!/usr/bin/env python3
# !/usr/bin/python3

import os, shutil

from suqc.CommandBuilder.VadereControlCommand import VadereControlCommand

from suqc import (
    CoupledDictVariation,
)
from suqc.utils.SeedManager.VadereSeedManager import VadereSeedManager

run_local = True

if os.getenv("CROWNET_HOME") is None:
    crownet_root = os.path.abspath(f"{__file__}/../../../../../..")
    if os.path.basename(crownet_root) == "crownet":
        os.environ["CROWNET_HOME"] = crownet_root
        print(f"Add CROWNET_HOME = {crownet_root} to env variables.")
    else:
        raise ValueError(
            f"Please provide environmental variable CROWNET_HOME = path/to/crownet/repo."
        )


def main(parameter="default", quantity_of_interest="default"):
    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

    ## Define the simulation to be used
    # A rover simulation is defined by an "omnetpp.ini" file and its corresponding directory.
    # Use following *.ini file:

    path2ini = os.path.join(
        os.environ["CROWNET_HOME"],
        "crownet/simulations/guiding_crowds_test/omnetpp.ini",
    )

    ## Define parameters and sampling method
    # parameters
    dependent_parameters = [
        {'vadere': {'sources.[id==1].distributionParameters': [0.0375]}},
        {'vadere': {'sources.[id==1].distributionParameters': [0.05]}}
    ]

    # number of repitions for each sample
    reps = 1

    # sampling
    par_var = VadereSeedManager(par_variations=dependent_parameters,
                                rep_count=reps,
                                vadere_fixed=False) \
        .get_new_seed_variation()

    ## Define the quantities of interest (simulation output variables)
    # Make sure that corresponding post processing methods exist in the run_script2.py file

    if quantity_of_interest == "default":
        quantity_of_interest = [
            "overlapCount.txt",
        ]

    # define tag of omnet and vadere docker images, see https://sam-dev.cs.hm.edu/rover/rover-main/container_registry/
    model = VadereControlCommand() \
        .create_vadere_container() \
        .control_use_local() \
        .with_control("control.py") \
        .control_argument("controller-type", "PingPong") \
        .scenario_file("vadere/scenarios/test001.scenario") \
        .qoi(quantity_of_interest) \
        .experiment_label("out")

    setup = CoupledDictVariation(
        ini_path=path2ini,
        config="final",
        parameter_dict_list=par_var,
        qoi=quantity_of_interest,
        model=model,
        post_changes=None,
        output_path=os.path.dirname(output_folder),
        output_folder=output_folder,
        remove_output=False,
        env_remote=None
    )

    if os.environ["CROWNET_HOME"] is None:
        raise SystemError(
            "Please add ROVER_MAIN to your system variables to run a rover simulation."
        )

    if run_local:
        par_var, data = setup.run(1)
    else:
        par_var, data = setup.remote(-1)

    # Save results
    summary = output_folder + "_summary"
    if os.path.exists(summary):
        shutil.rmtree(summary)

    os.makedirs(summary)

    par_var.to_csv(os.path.join(summary, "parameters.csv"))
    for q in quantity_of_interest:
        data.to_csv(os.path.join(summary, f"{q}"))

    print("All simulation runs completed.")


if __name__ == "__main__":
    main()
