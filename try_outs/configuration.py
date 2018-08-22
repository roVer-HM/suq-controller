#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import os
import json
import glob
import copy
import argparse
import sys

sys.path.append(os.path.abspath("./.."))  # TODO: keep as long there is the folder "try_outs"

import pandas as pd

from shutil import copyfile, rmtree

from try_outs.utils.general import user_query_yes_no, user_query_numbered_list, get_git_hash

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


# TODO: make a central file of all the (config-) filenames, set by suq-controller!
# relative path of this file:
SRC_PATH = os.path.relpath(os.path.join(__file__, os.pardir))
SUQ_CONFIG_PATH = os.path.join(SRC_PATH, "suq_config.json")

# configuration of the suq-controller
DEFAULT_SUQ_CONFIG = {"container_paths": [os.path.join(SRC_PATH, "envs")],
                      "models": dict()}

# configuration saved with each environment
DEFAULT_SC_CONFIG = {"git_hash_at_creation": "not_set", "model": None}


def _convert_to_json(s):  # TODO: put in utils
    return json.loads(s)


def store_config(d):        # TODO: put in utils
    with open(SUQ_CONFIG_PATH, "w") as outfile:
        json.dump(d, outfile, indent=4)


def select_env_path():
    paths = get_con_paths()
    if len(paths) == 1:
        return paths[0]
    else:
        return user_query_numbered_list(paths)


def get_suq_config(reset_default=False):
    if reset_default or not os.path.exists(SUQ_CONFIG_PATH):
        with open(SUQ_CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_SUQ_CONFIG, f, indent=4)
        print(f"INFO: Writing default configuration to \n {SUQ_CONFIG_PATH} \n")
        return DEFAULT_SUQ_CONFIG
    else:
        with open(SUQ_CONFIG_PATH, "r") as f:
            config_file = f.read()
        return _convert_to_json(config_file)


def get_model_location(name):
    config = get_suq_config()
    return config["models"][name]


def add_new_model(name, location):
    config = get_suq_config()

    if name in config["models"]:

        if os.path.abspath(location) == os.path.abspath(config["models"][name]):
            return  # is anyway the same path

        if not user_query_yes_no(question=f"The name '{name}' already exists in the lookup table. Do you want to "
                                          f"update the path? \n "
                                          f"{config['models'][name]} --> {location}"):
            return  # not updating the path

    assert os.path.exists(location), f"The location {os.path.abspath(location)} is does not exist."

    config["models"][name] = location
    store_config(config)


def remove_model(name):
    assert name is not None
    config = get_suq_config()
    del config["models"][name]
    store_config(config)


def get_models():
    config = get_suq_config()
    return config["models"]


def new_con_path(p):
    config = get_suq_config()
    assert p not in config["container_paths"]
    assert os.path.exists(p) and isinstance(p, str)
    config["container_paths"].append(p)
    store_config(config)


def remove_con_path(p):
    config = get_suq_config()
    config["container_paths"].remove(p)
    store_config(config)


def get_con_paths():
    return get_suq_config()["container_paths"]


def remove_environment(env_folder):
    if user_query_yes_no(question=f"Are you sure you want to remove the current environment? Path: \n {env_folder}"):
        rmtree(env_folder)
        return True
    else:
        return False


def create_environment(name, sc_basis_file, model, env_path, replace=False):
    # check the given .scenario file
    assert os.path.isfile(sc_basis_file), "Filepath to .scenario does not exist"
    assert sc_basis_file.split(".")[-1] == "scenario", "File has to be a VADERE '*.scenario' file"

    # Check if environment already exists
    target_path = os.path.join(env_path, name)

    if replace and os.path.exists(target_path):
        if not remove_environment(target_path):
            print("Aborting to create a new scenario.")
            return

    # Create new environment folder
    os.mkdir(target_path)

    # FILL IN THE STANDARD FILES IN THE NEW SCENARIO:

    # copy the .scenario file to the new folder
    filename = os.path.basename(sc_basis_file)
    copyfile(sc_basis_file, os.path.join(target_path, filename))

    # Create and store the configuration file to the new folder
    cfg = copy.deepcopy(DEFAULT_SC_CONFIG)

    assert model in get_models(), f"Set model {model} is not listed in configured models {get_models()}"

    cfg["model"] = model
    cfg["git_hash_at_creation"] = get_git_hash()[0]

    with open(os.path.join(target_path, "sc_config.json"), 'w') as outfile:
        json.dump(cfg, outfile, indent=4)

    # Create the 'vadere_scenarios' folder
    os.mkdir(os.path.join(target_path, "vadere_scenarios"))


def get_all_envs(env_path):
    return os.listdir(env_path)


def get_all_paths_with_envname(env_name):
    container_paths = get_suq_config()["container_paths"]
    paths_with_scenario = list()

    for p in container_paths:
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
        model_path = get_model_location(model_name)
        return os.path.abspath(model_path)

    def path_scenario_variation_folder(self):  # TODO: define 'vadere_scenarios' somewhere in a variable
        rel_path = os.path.join(self.env_path, "vadere_scenarios")
        return os.path.abspath(rel_path)

    def path_parid_table_file(self):
        return os.path.join(self.env_path, "parid_lookup.csv")

    def parid_table(self):
        return pd.read_csv(self.path_parid_table_file())

    def get_vadere_scenario_basis_file(self):
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


# TODO: Write tests for the CLI!
class CLI(object):

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="With this CLI you can configure the suq-controller. This includes things that mostly only "
                        "have to set up once, i.e. actions that are not necessarily required to call each evaluation "
                        "run of either the Surrogate Model or Uncertainty Quantification. \n"
                        "'container'\n"
                        "An container is the parent folder of environments.\n"
                        "'environment'\n"
                        "An environment consists of all relevant content to run parameter variations on VADERE "
                        "scenarios.")

        self.parser.add_argument("--new-con-path", nargs=1, default=None,
                                 metavar="CONTAINER_PATH",
                                 help="Set a new path to a container where the 'environments' are located.")

        self.parser.add_argument("--rem-con-path", nargs=1, default=None,
                                 metavar="CONTAINER_PATH",
                                 # TODO: solve issue with relative/absolute paths
                                 help="Remove a path to a container where 'environments' are located. The path has "
                                      "to be the same as displayed when running --show-env-paths.")

        self.parser.add_argument("--show-con-paths", default=False, action="store_true",
                                 help="Show all container paths where 'environments' are located")

        self.parser.add_argument("--con-path", default="select",
                                 help="Set the container path. Together with the environment name, this uniquely "
                                      "identifies the path to the environment (con-path + name). If not given, the path"
                                      "can be selected with the command line.")

        self.parser.add_argument("--show-envs", default=False, action="store_true",
                                 help="Flag to show all environments located in an container path.")

        self.parser.add_argument("--new-env", nargs=3, default=None,
                                 metavar=("ENV_NAME", "PATH_BASIS_FILE", "MODEL_NAME"),
                                 help="Create a new environment. The basis file path has to be a '.scneario' file.")

        self.parser.add_argument("--rem-env", nargs=1, default=None,
                                 metavar="NAME",
                                 help="Remove environment. The container can be selected with --env-path or can be "
                                      "selected with the command line.")

        self.parser.add_argument("--show-models", default=False, action="store_true", help="Flag to display all models")

        self.parser.add_argument("--new-model", nargs=2,
                                 metavar=("NAME", "PATH_MODEL"),
                                 help="Set new model. Currently only *.jar models are supported")
        self.parser.add_argument("--rem-model", nargs=1, metavar=("NAME"), help="Remove model by name.")

        self.opts = self.parser.parse_args()

    def _select_env_path(self):
        if self.opts.env_path == "select":
            path = select_env_path()
        else:
            path = self.opts.env_path[0]
            # TODO: there is a problem with relative / absolute paths, maybe this should be handled in a separate function
            assert path in get_con_paths()

        assert os.path.exists(path)
        return path

    def run_user_options(self):

        # --new-con-env
        if self.opts.new_con_path is not None:
            path = self.opts.new_env_path[0]
            new_con_path(path)

        # --rem-con-path [PATH]
        if self.opts.rem_con_path is not None:
            remove_con_path(self.opts.rem_env_path[0])

        # --show-con-paths
        if self.opts.show_con_paths:
            print(get_con_paths())

        # --show-envs
        if self.opts.show_envs:
            path = self._select_env_path()
            print(get_all_envs(path))

        # --new-env [NAME_NEW_ENV, PATH_TO_SCENARIO FILE, MODEL]
        if self.opts.new_env is not None:
            path = self._select_env_path()
            create_environment(name=self.opts.new_env[0],
                               sc_basis_file=self.opts.new_env[1],
                               model=self.opts.new_env[2],
                               env_path=path,
                               replace=True)

        # --rem-env [NAME_REM_ENV]
        if self.opts.rem_env is not None:
            path = self._select_env_path()
            target_path = os.path.join(path, self.opts.rem_env[0])
            remove_environment(target_path)

        # --show-models
        if self.opts.show_models:
            print(get_models())

        # --new-model [NAME, PATH]
        if self.opts.new_model:
            add_new_model(self.opts.new_model[0], self.opts.new_model[1])

        # --rem-model [NAME]
        if self.opts.rem_model:
            remove_model(self.opts.rem_model[0])


CLI().run_user_options()

#python3 configuration.py env

