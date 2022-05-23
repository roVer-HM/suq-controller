from __future__ import annotations
import json
import os
from suqc.parameter.sampling import ParameterVariationBase
from suqc.utils.single_scenario_p import SingleScenarioProvider



class VariationBasedScenarioProvider(SingleScenarioProvider):

    def __init__(self, env_path: str, par_var: ParameterVariationBase) -> None:
        super().__init__(env_path)
        self.scenario_dict: dict = par_var.get_items("omnet", "**.vadereScenarioPath")
        for k in self.scenario_dict.keys():
            val = self.scenario_dict[k]
            val = os.path.split(str(val).replace('"', ''))[-1]
            self.scenario_dict[k] = os.path.join(self.env_path, val)

    def get_base_scenario_path(self, parameter_id: int =-1, run_id: int = -1) -> str:
        """ return ONE base scenario file path. Will ignore given variation."""
        if parameter_id == -1 or run_id == -1 or (parameter_id, run_id) not in self.scenario_dict:
            return super().get_base_scenario_path()
        else:
            return self.scenario_dict[(parameter_id, run_id)]


    def get_base_scenario(self, parameter_id: int = -1, run_id: int = -1) -> dict:
        if (parameter_id, run_id) not in self.scenario_dict:
            return super().get_base_scenario(parameter_id, run_id) 
        else: 
            with open(self.scenario_dict[(parameter_id, run_id)], "r") as f:
                basis_file = json.load(f)
            return basis_file