#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import os

from try_outs.parameter import ParameterVariation, ScenarioVariationCreator
from try_outs.environment import EnvironmentManager

import subprocess

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class Query(object):
    def __init__(self, env_manager: EnvironmentManager):
        self._env_man = env_manager

    def query(self):
        for scfp in self._env_man.get_vadere_scenario_variations():
            bname = os.path.basename(scfp)
            output_path = "".join([os.path.abspath(bname), "_output"])
            os.mkdir(output_path)  # TODO: handle what if already exists...
            self._simulate(scfp, output_path)

    def _simulate(self, scenario_fp, output_path):
        model_path = self._env_man.get_cfg_value(key="model")
        subprocess.call(["java", "-jar", model_path, scenario_fp, output_path, "-suq"])


if __name__ == "__main__":
    em = EnvironmentManager.set_by_env_name("chicken")
    Query(em)
