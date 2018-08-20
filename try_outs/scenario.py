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


def remove_scenario(sc_folder):
    if user_query_yes_no(question=f"Are you sure you want to overwrite the scenario? \n {sc_folder}"):
        rmtree(sc_folder)
        return True
    else:
        return False


def create_scenario(sc_folder, sc_basis_file, model, replace=False):
    # check the given .scenario file
    assert os.path.isfile(sc_basis_file), "Filepath to .scenario does not exist"
    assert sc_basis_file.split(".")[-1] == "scenario", "File has to be a VADERE '*.scenario' file"

    # Check if scenario already exists
    if replace and os.path.exists(sc_folder):
        if not remove_scenario(sc_folder):
            print("Aborting to create a new scenario.")
            return

    # Create new scneario folder
    os.mkdir(sc_folder)

    # FILL IN THE FILES IN THE NEW SCENARIO:

    # copy the scenario file to the new folder
    filename = os.path.basename(sc_basis_file)
    copyfile(sc_basis_file, os.path.join(sc_folder, filename))

    # Create and store the configuration file to the new folder
    cfg = copy.deepcopy(DEFAULT_SC_CONFIG)
    cfg["model"] = model

    with open(os.path.join(sc_folder, "sc_config.json"), 'w') as outfile:
        json.dump(cfg, outfile, indent=4)


class ScenarioManager(object):

    # TODO: make scenario creation in an extra class -- this file should *only* manage scenarios

    def __init__(self, scenario_path=None):
        if scenario_path is None:
            list_paths = get_suq_config()["scenario_paths"]

            if len(list_paths) > 1:
                self._scpath = user_query_numbered_list(list_paths)
            else:
                self._scpath = list_paths[0]
        else:
            self._scpath = scenario_path

    @classmethod
    def setscname(cls, scname):
        sm = ScenarioManager()
        paths = sm._get_all_paths_with_scname(scname)
        if len(paths) > 1:
            path = user_query_numbered_list(paths)
        else:
            path = paths[0]

        return ScenarioManager(path)

    @classmethod
    def setscpath(cls, scpath):
        return ScenarioManager(scenario_path=scpath)

    def _get_sc_names(self, p):
        return os.listdir(p)  # the folder names are the scenario names

    def _get_all_sc_names(self):
        names = list()
        for p in self._scpath:
            names.append(self._get_sc_names(p))
        return names

    def _get_all_paths_with_scname(self, scname):
        sc_paths = get_suq_config()["scenario_paths"]
        paths_with_scenario = list()

        for p in sc_paths:
            if scname in self._get_sc_names(os.path.abspath(p)):
                paths_with_scenario.append(p)
        return paths_with_scenario

    def get_scfolder_path(self, scname):
        return os.path.join(self._scpath, scname)  # TODO: fix, after merged code from uni

    def get_scvadere_folder(self, scname):  # TODO: define 'vadere_scenarios' somehwere in a variable
        rel_path = os.path.join(self.get_scfolder_path(scname), "vadere_scenarios")
        return os.path.abspath(rel_path)

    def get_basis_file(self, sc_name):
        sc_files = glob.glob(os.path.join(self._scpath, sc_name, "*.scenario"))
        assert len(sc_files) == 1, "Multiple .scenario files found..."

        with open(sc_files[0], "r") as f:
            scenario_content = json.load(f)

        return scenario_content


if __name__ == "__main__":
    pass
