#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import json
import glob
import copy
import os
import pandas as pd

from suqc.paths import Paths as pa

from shutil import copyfile, rmtree
from suqc.utils.general import user_query_yes_no, user_query_numbered_list, get_git_hash, create_folder
from suqc.utils.dict_utils import deep_dict_lookup

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------

# configuration of the suq-controller
DEFAULT_SUQ_CONFIG = {"container_paths": [os.path.join(pa.path_src_folder(), "envs")],
                      "models": dict()}

# configuration saved with each environment
DEFAULT_SC_CONFIG = {"git_hash_at_creation": "not_set", "model": None}


def add_new_model(name, filepath):

    if not os.path.exists(filepath):
        raise FileNotFoundError("File {filepath} does not exist! Either check 'filepath' or consider using absolute "
                                "paths.")

    dst_fp = os.path.join(pa.path_models_folder(), os.path.basename(filepath))

    if os.path.exists(dst_fp):
        raise FileExistsError(f"Model file '{os.path.basename(dst_fp)}' exists already!")

    config = _get_suq_config()

    if name in config["models"].keys():
        raise ValueError(f"Model with name '{name}' already exists.")

    print(f"INFO: The model file {filepath} is copied to {dst_fp}.")

    copyfile(src=filepath, dst=dst_fp)
    config["models"][name] = os.path.basename(dst_fp)
    _store_config(config)


def remove_model(name):
    assert name is not None
    config = _get_suq_config()
    # remove from config file:
    try:
        filename = config["models"][name]
        del config["models"][name]
        _store_config(config)

        # remove file in models path
        os.remove(os.path.join(pa.path_models_folder(), filename))

    except KeyError:
        print(f"WARNING: The model {name} is not present. List of all current model names: {config['models'].keys()}")
    except FileNotFoundError:
        print(f"WARNING: The corresponding file with filename {filename} is not present in {pa.path_models_folder()}. "
              f"The model with {name} was removed from the config file.")


def new_con_path(p):
    config = _get_suq_config()
    assert p not in config["container_paths"]
    assert os.path.exists(p) and isinstance(p, str)
    config["container_paths"].append(p)
    _store_config(config)


def remove_con_path(p):
    config = _get_suq_config()
    config["container_paths"].remove(p)
    _store_config(config)


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

    if model not in _all_model_names():
        raise ValueError("Set model {model} is not listed in configured models {_all_model_names()}")

    cfg["model"] = model
    cfg["git_hash_at_creation"] = get_git_hash()[0]

    with open(os.path.join(target_path, "sc_config.json"), 'w') as outfile:
        json.dump(cfg, outfile, indent=4)

    # Create the 'vadere_scenarios' folder
    os.mkdir(os.path.join(target_path, "vadere_scenarios"))


def get_con_path():
    path = _get_suq_config()["container_paths"]
    assert len(path) == 1, "Currently only a single container path is supported"
    assert os.path.exists(path), "The path does not exist. Please run the command setup_folders.py given in the " \
                                 "software repository"
    return path[0]


def _all_model_names():
    config = _get_suq_config()
    return config["models"].keys()


def _store_config(d):
    with open(pa.path_suq_config_file(), "w") as outfile:
        json.dump(d, outfile, indent=4)


def _get_suq_config(reset_default=False):
    if reset_default or not os.path.exists(pa.path_suq_config_file()):
        with open(pa.path_suq_config_file(), "w") as f:
            json.dump(DEFAULT_SUQ_CONFIG, f, indent=4)
        print(f"INFO: Writing default configuration to \n {pa.path_suq_config_file()} \n")
        return DEFAULT_SUQ_CONFIG
    else:
        with open(pa.path_suq_config_file(), "r") as f:
            config_file = f.read()
        return json.loads(config_file)


def _get_model_location(name):
    config = _get_suq_config()
    path = os.path.join(pa.path_models_folder(), config["models"][name])

    if not os.path.exists(path):
        raise FileNotFoundError(f"Model {path} not found.")

    return path


def _get_all_envs(env_path):
    return os.listdir(env_path)


class EnvironmentManager(object):

    def __init__(self, name):
        con_path = get_con_path()

        self.env_path = os.path.join(con_path, name)
        if not os.path.exists(self.env_path):
            raise FileNotFoundError(f"Environment {self.env_path} does not exist")

    def get_model_path(self):
        # look up set model in environment
        model_name = self.get_cfg_value(key="model")
        # return the value from the suq-configuration
        model_path = _get_model_location(model_name)
        return os.path.abspath(model_path)

    def get_scenario_variation_path(self):
        rel_path = os.path.join(self.env_path, "vadere_scenarios")
        return os.path.abspath(rel_path)

    def get_output_path(self, sc_name, create):
        output_path = os.path.join(self.get_scenario_variation_path(), "".join([sc_name, "_output"]))
        if create:
            create_folder(output_path)
        return output_path

    def get_path_scenario_variation(self, par_id):
        return os.path.join(self.get_scenario_variation_path(), self.get_scenario_variation_filename(par_id))

    def save_scenario_variation(self, par_id, content):
        fp = self.get_path_scenario_variation(par_id)
        assert not os.path.exists(fp), f"File {fp} already exists!"

        with open(fp, "w") as outfile:
            json.dump(content, outfile, indent=4)
        return fp

    def get_cfg_value(self, key):
        return self.get_cfg_file()[key]

    def get_cfg_file(self):
        fp = os.path.join(self.env_path, "sc_config.json")
        with open(os.path.abspath(fp), "r") as file:
            js = json.load(file)
        return js

    def path_parid_table_file(self):
        return os.path.join(self.env_path, "parid_lookup.csv")

    def parid_table(self):
        return pd.read_csv(self.path_parid_table_file())

    def get_vadere_scenario_basis_file(self):
        sc_files = glob.glob(os.path.join(self.env_path, "*.scenario"))
        assert len(sc_files) == 1, "None or too many .scenario files found in environment."

        with open(sc_files[0], "r") as f:
            basis_file = json.load(f)
        return basis_file

    def get_value_basis_file(self, key):
        j = self.get_vadere_scenario_basis_file()
        return deep_dict_lookup(j, key, check_final_leaf=False, check_unique_key=True)

    def get_scenario_variation_filename(self, par_id):
        return "".join([str(par_id).zfill(10), ".scenario"])

    def parid_from_scenario_path(self, path):
        sc_name = os.path.basename(path).split(".scenario")[0]
        return int(sc_name)

    def get_vadere_scenario_name(self, sc_path):

        if not os.path.exists(sc_path):
            raise FileNotFoundError(f"Scenario file {sc_path} not found.")

        required_prefix = "scenario"

        try:
            fname, prefix = os.path.basename(sc_path).split(".")
        except ValueError:
            raise ValueError("Invalid file naming ({sc_path}), only one point is allowed in the filename.")

        if prefix != required_prefix:
            raise ValueError(f"A valid VADERE scenario file has to end with file ending '.{required_prefix}'")

        return fname

    def get_vadere_scenario_variations(self):
        sc_folder = self.get_scenario_variation_path()
        sc_files = glob.glob(os.path.join(sc_folder, "*.scenario"))
        return [[self.parid_from_scenario_path(i), i] for i in sc_files]

    def get_nr_variations(self):
        return len(self.get_vadere_scenario_variations())

if __name__ == "__main__":
    #add_new_model("vadere1", "./vadere-console1.jar")
    remove_model("vadere1")