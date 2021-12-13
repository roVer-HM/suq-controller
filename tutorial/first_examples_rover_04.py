#!/usr/bin/env python3
# !/usr/bin/python3

import sys

from suqc.CommandBuilder.VadereOppControlCommand import VadereOppControlCommand

from suqc.CommandBuilder.VadereOppCommand import VadereOppCommand

from suqc.utils.SeedManager.OmnetSeedManager import OmnetSeedManager
from tutorial.imports import *

# This is just to make sure that the systems path is set up correctly, to have correct imports, it can be ignored:

sys.path.append(os.path.abspath("."))
sys.path.append(os.path.abspath(".."))

run_local = True
###############################################################################################################
# Usecase: Set yourself the parameters you want to change. Do this by defining a list of dictionaries with the
# corresponding parameter. Again, the Vadere output is deleted after all scenarios run.


if __name__ == "__main__":
    output_folder = os.path.join(os.getcwd(), "first_examples_rover_04")
    ## Define the simulation to be used
    # A rover simulation is defined by an "omnetpp.ini" file and its corresponding directory.
    # Use following *.ini file:

    path2ini = os.path.join(
        os.environ["CROWNET_HOME"],
        "crownet/simulations/route_choice_app/omnetpp.ini",
    )

    ## Define parameters and sampling method
    # parameters
    # number of repetitions for each sample
    reps = 1

    # sampling
    par_var = [{'omnet': {'sim-time-limit': '10s'}},
               {'omnet': {'sim-time-limit': '20s'}}]
    par_var = OmnetSeedManager(par_variations=par_var, rep_count=reps, vadere_fixed=True, omnet_fixed=True) \
        .get_new_seed_variation()

    ## Define the quantities of interest (simulation output variables)
    # Make sure that corresponding post processing methods exist in the run_script2.py file

    qoi = ["densities.txt"]

    # define tag of omnet and vadere docker images, see https://sam-dev.cs.hm.edu/rover/rover-main/container_registry/

    model = VadereOppControlCommand() \
        .create_vadere_container() \
        .vadere_tag("latest") \
        .omnet_tag("latest") \
        .qoi(qoi) \
        .experiment_label("output") \
        .with_control("control.py") \
        .control_argument("controller-type", "OpenLoop") \
        .opp_argument("-c", "final")

    setup = CoupledDictVariation(
        ini_path=path2ini,
        config="final",
        parameter_dict_list=par_var,
        qoi=qoi,
        model=model,
        post_changes=None,
        output_path=path2tutorial,
        output_folder=output_folder,
        remove_output=False,
        env_remote=None,
    )
    setup.override_run_script_name("run_script_with_omnet.py")

    if os.environ["CROWNET_HOME"] is None:
        raise SystemError(
            "Please add ROVER_MAIN to your system variables to run a rover simulation."
        )

    if run_local:
        par_var, data = setup.run(1)
    else:
        par_var, data = setup.remote(-1)

    # Save results
    summary = output_folder + "_df"
    if os.path.exists(summary):
        shutil.rmtree(summary)

    os.makedirs(summary)

    par_var.to_csv(os.path.join(summary, "parameters.csv"))
    data.to_csv(os.path.join(summary, f"{qoi[0]}"))

    print("All simulation runs completed.")
