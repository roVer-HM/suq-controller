#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import glob
import copy
import os
import json

import pandas as pd

from shutil import copyfile, rmtree

import try_outs.configuration as suqcfg
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
    cfg = copy.deepcopy(suqcfg.DEFAULT_SC_CONFIG)
    cfg["model"] = model

    with open(os.path.join(env_folder, "sc_config.json"), 'w') as outfile:
        json.dump(cfg, outfile, indent=4)

    # Create the 'vadere_scenarios' folder
    os.mkdir(os.path.join(env_folder, "vadere_scenarios"))


def get_all_paths_with_envname(env_name):
    env_paths = suqcfg.get_suq_config()["env_paths"]
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
        self.env_path = env_path

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

    def get_cfg_value(self, key):
        fp = os.path.join(self.env_path, "sc_config.json")
        with open(os.path.abspath(fp), "r") as file:
            js = json.load(file)
        return js[key]

    def get_model_path(self):
        # look up set model in environment
        model_name = self.get_cfg_value(key="model")
        # return the value from the suq-configuration
        model_path = suqcfg.get_model_location(model_name)
        return os.path.abspath(model_path)

    def path_scenario_variation_folder(self):  # TODO: define 'vadere_scenarios' somewhere in a variable
        rel_path = os.path.join(self.env_path, "vadere_scenarios")
        return os.path.abspath(rel_path)

    def path_parid_table_file(self):
        return os.path.join(self.env_path, "parid_lookup.csv")

    def parid_table(self):
        return pd.read_csv(self.path_parid_table_file())

    def get_vadere_scenario_basis_file(self, sc_name):
        sc_files = glob.glob(os.path.join(self.env_path, "*.scenario"))
        assert len(sc_files) == 1, "None or too many .scenario files found..."

        with open(sc_files[0], "r") as f:
            basis_file = json.load(f)
        return basis_file

    def get_vadere_scenario_variations(self):
        sc_folder = self.path_scenario_variation_folder()
        sc_files = glob.glob(os.path.join(sc_folder, "*.scenario"))
        sc_files.sort()
        return sc_files


if __name__ == "__main__":
    create_environment(env_folder="envs/corner", sc_basis_file="rimea_06_corner.scenario", model="vadere",
                       replace=True)
