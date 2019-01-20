#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import json
import glob
import subprocess
import time
import os

from shutil import copyfile, rmtree
from typing import *

import pandas as pd

from suqc.paths import Paths as pa
from suqc.utils.general import user_query_yes_no, get_current_suqc_state, create_folder
from suqc.utils.dict_utils import deep_dict_lookup

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------

# configuration of the suq-controller
DEFAULT_SUQ_CONFIG = {"container_path": os.path.join(pa.path_src_folder(), "envs"),
                      "server": {
                          "host": "",
                          "user": "",
                          "port": -1
                      }}

def _store_config(d):
    with open(pa.path_suq_config_file(), "w") as outfile:
        json.dump(d, outfile, indent=4)

def get_suq_config():
    if not os.path.exists(pa.path_suq_config_file()):
        with open(pa.path_suq_config_file(), "w") as f:
            json.dump(DEFAULT_SUQ_CONFIG, f, indent=4)
        print(f"WARNING: Config did not exist. Writing default configuration to \n {pa.path_suq_config_file()} \n")
        return DEFAULT_SUQ_CONFIG
    else:
        with open(pa.path_suq_config_file(), "r") as f:
            config_file = f.read()
        return json.loads(config_file)


def store_server_config(host: str, user: str, port: int):
    cfg = get_suq_config()
    cfg["server"]["host"] = host
    cfg["server"]["user"] = user
    cfg["server"]["port"] = port
    _store_config(cfg)


def default_models_path():
    path = pa.path_models_folder()
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model {path} not found.")
    return path


class VadereConsoleWrapper(object):

    def __init__(self, model_path: str):
        self.jar_path = model_path
        if not os.path.exists(self.jar_path):
            raise FileExistsError(f"Vadere console file {self.jar_path} does not exist.")

    def run_simulation(self, scenario_fp, output_path):
        start = time.time()
        ret_val = subprocess.call(["java", "-jar", self.jar_path, "suq", "-f", scenario_fp, "-o", output_path])
        return ret_val, time.time() - start

    @classmethod
    def from_default_models(cls, model):
        if not model.endswith(".jar"):
            model = ".".join([model, "jar"])
        return cls(os.path.join(default_models_path(), model))

    @classmethod
    def from_model_path(cls, model_path):
        return cls(model_path)

    @classmethod
    def from_new_compiled_package(cls, src_path=None):
        pass  # TODO: use default src_path


class EnvironmentManager(object):

    def __init__(self, env_name: str, model: Union[VadereConsoleWrapper, str]):
        self.name = env_name
        self.env_path = self.environment_path(self.name)

        print(f"INFO: Set environment path to {self.env_path}")
        if not os.path.exists(self.env_path):
            raise FileNotFoundError(f"Environment {self.env_path} does not exist")

        # TODO: in future maybe infer also if it is the path to Vadere src (the inference can be completely impemented
        #  in the wrapper)
        if isinstance(model, str):
            if os.path.exists(model):
                self.model = VadereConsoleWrapper.from_model_path(model)
            else:
                self.model = VadereConsoleWrapper.from_default_models(model)
        else:
            self.model = model

        self._scenario_basis = None

    @property
    def scenario_basis(self):
        if self._scenario_basis is None:
            sc_files = glob.glob(os.path.join(self.env_path, "*.scenario"))
            assert len(sc_files) == 1, "None or too many .scenario files found in environment."

            with open(sc_files[0], "r") as f:
                basis_file = json.load(f)
            self._scenario_basis = basis_file

        return self._scenario_basis

    @classmethod
    def create_if_not_exist(cls, env_name: str, basis_scenario: Union[str, dict],
                           model: Union[VadereConsoleWrapper, str]):
        target_path = cls.environment_path(env_name)
        if os.path.exists(target_path):
            existing = cls(env_name, model)

            # TODO: maybe it is good to compare if the handled file is the same as the existing
            #exist_basis_file = existing.get_vadere_scenario_basis_file()
            return existing
        else:
            return cls.create_environment(env_name, basis_scenario, model)

    @classmethod
    def create_environment(cls, env_name: str, basis_scenario: Union[str, dict],
                           model: Union[VadereConsoleWrapper, str], replace: bool = False):

        # Check if environment already exists
        target_path = cls.environment_path(env_name)

        if replace and os.path.exists(target_path):
            if not cls.remove_environment(env_name):
                print("Aborting to create a new scenario.")
                return

        # Create new environment folder
        os.mkdir(target_path)

        if isinstance(basis_scenario, str):  # assume that this is a path

            assert os.path.isfile(basis_scenario), "Filepath to .scenario does not exist"
            assert basis_scenario.split(".")[-1] == "scenario", "File has to be a VADERE '*.scenario' file"

            with open(basis_scenario, "r") as file:
                basis_scenario = file.read()

        basis_fp = os.path.join(target_path, f"BASIS_{env_name}.scenario")

        # FILL IN THE STANDARD FILES IN THE NEW SCENARIO:
        with open(basis_fp, "w") as file:
            if isinstance(basis_scenario, dict):
                json.dump(basis_scenario, file, indent=4)
            else:
                file.write(basis_scenario)

        # Create and store the configuration file to the new folder
        cfg = dict()

        cfg["suqc_state"] = get_current_suqc_state()

        with open(os.path.join(target_path, "suqc_commit_hash.json"), 'w') as outfile:
            s = "\n".join(["commit hash at creation", get_current_suqc_state()])
            outfile.write(s)

        # Create the folder where the output is stored
        os.mkdir(os.path.join(target_path, "vadere_output"))

        return cls(env_name, model)

    @classmethod
    def remove_environment(cls, name, force=False):
        target_path = cls.environment_path(name)
        if force or user_query_yes_no(question=f"Are you sure you want to remove the current environment? Path: \n "
        f"{target_path}"):
            try:
                rmtree(target_path)
            except FileNotFoundError:
                print(f"INFO: Tried to remove environment {name}, but did not exist.")
            return True
        return False

    @staticmethod
    def environment_path(name):
        path = os.path.join(EnvironmentManager.get_container_path(), name)
        return path

    @staticmethod
    def get_container_path():

        if not pa.is_package_paths():
            rel_path = pa.path_src_folder()
        else:
            rel_path = ""

        path = get_suq_config()["container_path"]

        path = os.path.abspath(os.path.join(rel_path, path))
        assert os.path.exists(
            path), f"The path {path} does not exist. Please run the command setup_folders.py given in " \
            f"the software repository"
        return path

    def get_env_outputfolder_path(self):
        rel_path = os.path.join(self.env_path, "vadere_scenarios")
        return os.path.abspath(rel_path)

    def get_par_id_output_path(self, par_id, create):
        scenario_filename = self._scenario_variation_filename(par_id=par_id)
        scenario_filename = scenario_filename.replace(".scenario", "")
        output_path = os.path.join(self.get_env_outputfolder_path(), "".join([scenario_filename, "_output"]))
        if create:
            create_folder(output_path)
        return output_path

    def _scenario_variation_filename(self, par_id):
        return "".join([str(par_id).zfill(10), ".scenario"])

    def scenario_variation_path(self, par_id):
        return os.path.join(self.get_env_outputfolder_path(), self._scenario_variation_filename(par_id))

    def save_scenario_variation(self, par_id, content):
        fp = self.scenario_variation_path(par_id)
        assert not os.path.exists(fp), f"File {fp} already exists!"

        with open(fp, "w") as outfile:
            json.dump(content, outfile, indent=4)
        return fp

if __name__ == "__main__":
    pass
    #create_environment_from_file(name="fp_operator", filepath=
    #"/home/daniel/REPOS/vadere_projects/vadere/VadereModelTests/TestOSM/scenarios/New_Simple_FP.scenario",
    #                             model="vadere")