#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import os

from shutil import copyfile, rmtree

from try_outs.configuration import *

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class ScenarioManager(object):

    def __init__(self, scenario_path=None):
        if scenario_path is None:
            self._sc_paths = get_suq_config()["scenario_paths"]
        else:
            self._sc_paths = scenario_path

    def _get_sc_names(self, p):
        return os.listdir(p)  # the folder names are the scenario names

    def _get_all_sc_names(self):
        names = list()
        for p in self._sc_paths:
            names.append(self._get_sc_names(p))
        return names

    def _check_double_sc_names(self):
        pass

    def _fill_files_new_sc(self, scenario_fp, sc_folder, sc_config):

        # 1. the .scenario file
        assert os.path.isfile(scenario_fp), "Filepath to .scenario does not exist"
        assert scenario_fp.split(".")[-1] == ".scenario", "File has to be a VADERE .scenario file"

        filename = os.path.basename(scenario_fp)
        copyfile(scenario_fp, os.path.join(sc_folder, filename))

        # 2. the config file
        with open(os.path.join(sc_folder, "sc_config"), "w") as f:
            f.write(sc_config)

    def _create_sc_config(self, model):
        default_cfg = DEFAULT_SUQ_CONFIG
        default_cfg["model"] = model
        return default_cfg

    def _remove_scenario(self, folder_path):
        # TODO: this should be checked with user prompt whether to remove the existing folder
        rmtree(folder_path)

    def add_new_scenario(self, scenario_fp, name, model, replace=False):

        # TODO: for now a new scenario gets always saved in the first entry of the list, this should be changed (e.g. console prompt)
        target_sc_path = self._sc_paths[0]  # = parent folder of the scenario, where all scenarios are stored
        sc_folder = os.path.join(target_sc_path, name)

        if replace and os.path.exists(sc_folder):
            self._remove_scenario(sc_folder)

        assert name not in self._get_sc_names(target_sc_path), f"Scenario {name} exists already in: \n " \
                                                               f"{target_sc_path }"
        os.mkdir(sc_folder)

        sc_config = self._create_sc_config(model=model)
        self._fill_files_new_sc(scenario_fp, sc_folder, sc_config)


if __name__ == "__main__":
    sm = ScenarioManager()

    scfp = "/home/daniel/REPOS/vadere/suq-controller/try_outs/basic_1_chicken_osm1.scenario"
    sm.add_new_scenario(scfp, "chicken", "vadere", replace=True)
