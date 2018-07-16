#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import glob

from shutil import copyfile, rmtree

from try_outs.configuration import *
from try_outs.utils.general import user_query_yes_no, user_query_numbered_list

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class ScenarioManager(object):

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

    def _check_double_sc_names(self):
        pass

    def _fill_files_new_sc(self, scenario_fp, sc_folder, sc_config):

        # 1. the .scenario file
        assert os.path.isfile(scenario_fp), "Filepath to .scenario does not exist"
        assert scenario_fp.split(".")[-1] == "scenario", "File has to be a VADERE '*.scenario' file"

        filename = os.path.basename(scenario_fp)
        copyfile(scenario_fp, os.path.join(sc_folder, filename))

        # 2. the config file
        with open(os.path.join(sc_folder, "sc_config.json"), 'w') as outfile:
            json.dump(sc_config, outfile, indent=4)

    def _create_sc_config(self, model):
        default_cfg = DEFAULT_SC_CONFIG
        default_cfg["model"] = model
        return default_cfg

    def _remove_scenario(self, folder_path):
        if user_query_yes_no(question=f"Are you sure you want to overwrite the scenario? \n {folder_path}"):
            rmtree(folder_path)
            return True
        else:
            return False

    def get_scfolder_path(self, scname):
        return os.path.join(self._scpath, scname)  # TODO: fix, after merged code from uni

    def get_scvadere_folder(self, scname): # TODO: define 'vadere_scenarios' somehwere in a variable
        rel_path = os.path.join(self.get_scfolder_path(scname), "vadere_scenarios")
        return os.path.abspath(rel_path)

    def add_new_scenario(self, scenario_fp, scname, model, replace=False):

        # = parent folder of the scenario, where all scenarios are stored
        # target_sc_path = self._sc_path[0]

        scfolder = os.path.join(self._scpath, scname)

        if replace and os.path.exists(scfolder):
            if not self._remove_scenario(scfolder):
                print("Aborting to create a new scenario.")
                return

        assert scname not in self._get_all_sc_names(), f"Scenario {scname} exists already in: \n " \
                                                              f"{self._scpath}"
        os.mkdir(scfolder)

        sc_config = self._create_sc_config(model=model)
        self._fill_files_new_sc(scenario_fp, scfolder, sc_config)

    def get_vadere_scbasis_file(self, sc_name):
        sc_files = glob.glob(os.path.join(self._scpath, sc_name, "*.scenario"))
        assert len(sc_files) == 1, "Multiple .scenario files found..."

        with open(sc_files[0], "r") as f:
            scenario_content = json.load(f)

        return scenario_content


if __name__ == "__main__":
    sm = ScenarioManager()

    #scfp = os.path.join(SRC_PATH, "basic_1_chicken_osm1.scenario")
    #sm.add_new_scenario(scfp, "chicken", "vadere", replace=True)

    print(sm.get_scenario_file("chicken")["processWriters"])

