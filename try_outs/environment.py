#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import glob
import copy

from shutil import copyfile, rmtree

from try_outs.configuration import *
from try_outs.utils.general import user_query_yes_no, user_query_numbered_list

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


def remove_environment(sc_folder):
    if user_query_yes_no(question=f"Are you sure you want to overwrite the scenario? \n {sc_folder}"):
        rmtree(sc_folder)
        return True
    else:
        return False


def create_environment(env_folder, sc_basis_file, model, replace=False):
    # check the given .scenario file
    assert os.path.isfile(sc_basis_file), "Filepath to .scenario does not exist"
    assert sc_basis_file.split(".")[-1] == "scenario", "File has to be a VADERE '*.scenario' file"

    # Check if environment already exists
    if replace and os.path.exists(env_folder):
        if not remove_environment(env_folder):
            print("Aborting to create a new scenario.")
            return

    # Create new environment folder
    os.mkdir(env_folder)

    # FILL IN THE FILES IN THE NEW SCENARIO:

    # copy the .scenario file to the new folder
    filename = os.path.basename(sc_basis_file)
    copyfile(sc_basis_file, os.path.join(env_folder, filename))

    # Create and store the configuration file to the new folder
    cfg = copy.deepcopy(DEFAULT_SC_CONFIG)
    cfg["model"] = model

    with open(os.path.join(env_folder, "sc_config.json"), 'w') as outfile:
        json.dump(cfg, outfile, indent=4)

    # Create the 'vadere_scenarios' folder
    os.mkdir(os.path.join(env_folder, "vadere_scenarios"))


def get_all_paths_with_envname(env_name):
    env_paths = get_suq_config()["env_paths"]
    paths_with_scenario = list()

    for p in env_paths:
        if env_name in os.listdir(os.path.abspath(p)):
            paths_with_scenario.append(p)
    return paths_with_scenario

#def get_all_env_names():
#    names = list()
#    for p in self._env_path:
#        names.append(self._get_sc_names(p))
#    return names


class EnvironmentManager(object):

    def __init__(self, env_path):
        self._env_path = env_path

    @classmethod
    def set_by_env_name(cls, env_name):
        paths = get_all_paths_with_envname(env_name)
        if len(paths) > 1:
            path = user_query_numbered_list(paths)
        else:
            path = paths[0]
        path = os.path.abspath(os.path.join(path, env_name))
        assert os.path.exists(path)
        return EnvironmentManager(env_path=path)

    @classmethod
    def set_by_env_path(cls, env_path):
        return EnvironmentManager(env_path=env_path)

    def get_vadere_scenarios_folder(self):  # TODO: define 'vadere_scenarios' somewhere in a variable
        rel_path = os.path.join(self._env_path, "vadere_scenarios")
        return os.path.abspath(rel_path)

    def get_vadere_scenario_basis_file(self, sc_name):
        sc_files = glob.glob(os.path.join(self._env_path, "*.scenario"))
        assert len(sc_files) == 1, "None or too many .scenario files found..."

        with open(sc_files[0], "r") as f:
            basis_file = json.load(f)
        return basis_file


if __name__ == "__main__":
    create_environment(env_folder="envs/chicken", sc_basis_file="basic_1_chicken_osm1.scenario", model="vadere",
                       replace=True)
