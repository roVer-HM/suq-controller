#!/usr/bin/env python3

import sys

from suqc.CommandBuilder.JarCommand import JarCommand
from suqc.utils.git_utils import get_jar_file_from_vadere_repo, jar_path
from tutorial.imports import *

# This is just to make sure that the systems path is set up correctly, to have correct imports.
# (It can be ignored)

sys.path.append(
    os.path.abspath("testfolder")
)  # in case tutorial is called from the root directory
sys.path.append(os.path.abspath(""))  # in tutorial directly

run_local = True

###############################################################################################################
# Usecase: One parameter in the scenario is changed, for every independent the data is collected and returned.
# The Vadere output is deleted after all scenarios run.

# Example where the values of 'spawnNumber' are set to 100 and 101
if __name__ == "__main__":
    # Works on Linux operating system only

    # get_info_vadere_repo()  # Provide system variable VADERE !
    scenario_file = os.path.join(
        os.path.join(os.environ["CROWNET_HOME"], "vadere"),
        "Scenarios/Demos/Density_controller/scenarios/TwoCorridors_unforced.scenario",
    )

    # download jar file from git
    commit = "4b9008ff9df36a5e87f11ed49541e15263f857a3"
    branch = "master"
    jar_path = jar_path(path=path2tutorial, branch=branch, commit_hash=commit)
    if not os.path.exists(jar_path):
        get_jar_file_from_vadere_repo(path=path2tutorial, branch=branch,
                                      commit_hash=commit)

    jar_command = JarCommand(jar_file=jar_path) \
        .add_option("-enableassertions") \
        .main_class("suq")

    setup = SingleKeyVariation(  # path to a Vadere .scenario file (the one to sample)
        scenario_path=scenario_file,
        # parameter key to change
        key="sources.[id==2].spawnNumber",
        # values to set for the parameter
        values=np.arange(100, 102, dtype=int),
        # output file name to collect
        qoi="evacuationTime.txt",
        # path to Vadere console jar file or use
        # VadereConsoleWrapper for more options
        model=jar_command,
        # specify how often each scenario should run
        scenario_runs=1,
        # post changes can be used to apply changes to the scenario that are not part of the
        # sampling -- especially random seed setting. It is easy to define user based changes.
        post_changes=PostScenarioChangesBase(apply_default=True),
        # specify the path, where the results are written
        output_path=path2tutorial,
        # specify the folder to write vadere output files to
        output_folder="testfolder",
        # flag whether to remove the output_folder after the run
        remove_output=False,
    )

    if run_local:
        par_var, data = setup.run(njobs=-1)
    else:
        par_var, data = setup.remote(njobs=-1)

    print("---------------------------------------\n \n")
    print("ALL USED PARAMETER:")
    print(par_var)

    print("COLLECTED DATA:")
    print(data)
