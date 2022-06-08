
from __future__ import annotations
import glob
import json
import os
from suqc.utils.general import ScenarioProvider


class SingleScenarioProvider(ScenarioProvider):
    VADERE_SCENARIO_FILE_TYPE = ".scenario"
    
    def __init__(self, env_path: str) -> None:
        super().__init__(env_path)
        self._vadere_scenario_basis: str|None = None

    def get_base_scenario_path(self, parameter_id: int =-1, run_id: int = -1) -> str:
        """ return ONE base scenario file path. Will ignore given variation."""
        sc_files = glob.glob(
            os.path.join(self.env_path, f"*{self.VADERE_SCENARIO_FILE_TYPE}")
        )

        if len(sc_files) != 1:
            raise RuntimeError(
                f"None or too many '{self.VADERE_SCENARIO_FILE_TYPE}' files "
                "found in environment."
            )
        return sc_files[0]

    def get_base_scenario(self, parameter_id: int =-1, run_id: int = -1) -> dict:
        """ return ONE base scenario file content as json-dict. Will ignore given variation."""
        if self._vadere_scenario_basis is None:
            path_basis_scenario = self.get_base_scenario_path()

            with open(path_basis_scenario, "r") as f:
                basis_file = json.load(f)
            self._vadere_scenario_basis = basis_file

        return self._vadere_scenario_basis

