#!/usr/bin/env python3 

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

from suqc.configuration import EnvironmentManager
from suqc.parameter.parvariation import ParameterVariation
from suqc.qoi import QoIProcessor

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class SimulationDefinition(object):

    def __init__(self, env_man: EnvironmentManager, par_var: ParameterVariation, qoi: QoIProcessor):
        self.name = env_man.name
        self.basis_file = env_man.get_vadere_scenario_basis_file()
        self.model = env_man.get_cfg_value("model")
        self.par_var = par_var
        self.qoi = qoi