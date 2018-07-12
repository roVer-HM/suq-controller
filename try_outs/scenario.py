#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

from shutil import copyfile, rmtree

from try_outs.configuration import *
from try_outs.utils import user_query_yes_no, user_query_numbered_list

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

    def _get_all_paths_with_scname(self, scname):
        paths = list()
        for p in self._sc_paths:
            if scname in self._get_sc_names(p):
                paths.append(p)
        return paths

    def _check_double_sc_names(self):
        pass

    def _fill_files_new_sc(self, scenario_fp, sc_folder, sc_config):

        # 1. the .scenario file
        assert os.path.isfile(scenario_fp), "Filepath to .scenario does not exist"
        assert scenario_fp.split(".")[-1] == "scenario", "File has to be a VADERE *.scenario file"

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

    def add_new_scenario(self, scenario_fp, name, model, replace=False):

        # = parent folder of the scenario, where all scenarios are stored
        if len(self._sc_paths) > 1:
            target_sc_path = user_query_numbered_list(self._sc_paths)
        else:
            target_sc_path = self._sc_paths[0]

        sc_folder = os.path.join(target_sc_path, name)

        if replace and os.path.exists(sc_folder):
            if not self._remove_scenario(sc_folder):
                print("Aborting creating a new scenario.")
                return

        assert name not in self._get_sc_names(target_sc_path), f"Scenario {name} exists already in: \n " \
                                                               f"{target_sc_path }"
        os.mkdir(sc_folder)

        sc_config = self._create_sc_config(model=model)
        self._fill_files_new_sc(scenario_fp, sc_folder, sc_config)

    def get_scenario_file(self, sc_name):  # TODO: think about to set sc_name in __init__?
        with open("/home/daniel/REPOS/vadere_projects/suq-controller/try_outs/scenarios/chicken/basic_1_chicken_osm1.scenario", "r") as f:
            content = json.load(f)
        return content


if __name__ == "__main__":
    sm = ScenarioManager()

    scfp = os.path.join(SRC_PATH, "basic_1_chicken_osm1.scenario")
    sm.add_new_scenario(scfp, "chicken", "vadere", replace=True)
