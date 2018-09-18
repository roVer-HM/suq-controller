#!/usr/bin/env python3 

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

from suqc.configuration import EnvironmentManager
from suqc.parameter.sampling import ParameterVariation
from suqc.parameter.postchanges import ScenarioChanges

from suqc.utils.general import create_folder, remove_folder
from suqc.utils.dict_utils import change_dict

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class VadereScenarioCreation(object):

    def __init__(self, env_man: EnvironmentManager, par_var: ParameterVariation, sc_change: ScenarioChanges=None):
        self._env_man = env_man
        self._par_var = par_var
        self._sc_change = sc_change

    def _vars_object(self, pid, fp):
        return {"par_id": pid, "scenario_path": fp}

    def _create_new_vadere_scenario(self, scenario: dict, par_id: int, par_var: dict):

        par_var_scenario = change_dict(scenario, changes=par_var)

        if self._sc_change is not None:
            # Apply pre-defined changes to each scenario file
            final_scenario = self._sc_change.change_scenario(scenario=par_var_scenario, par_id=par_id, par_var=par_var)
        else:
            final_scenario = par_var_scenario

        return final_scenario

    def _save_vadere_scenario(self, par_id, s):
        fp = self._env_man.save_scenario_variation(par_id, s)
        return fp

    def generate_vadere_scenarios(self):

        target_path = self._env_man.get_scenario_variation_path()
        basis_scenario = self._env_man.get_vadere_scenario_basis_file()

        self._par_var.check_selected_keys(basis_scenario)

        remove_folder(target_path)
        create_folder(target_path)

        vars = list()
        for par_id, par_changes in self._par_var.par_iter():
            new_scenario = self._create_new_vadere_scenario(basis_scenario, par_id, par_changes)
            fp = self._save_vadere_scenario(par_id, new_scenario)
            vars.append(self._vars_object(par_id, fp))
        return vars