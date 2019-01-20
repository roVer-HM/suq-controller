#!/usr/bin/env python3 

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

from suqc.configuration import EnvironmentManager
from suqc.parameter.sampling import ParameterVariation
from suqc.parameter.postchanges import ScenarioChanges
from suqc.qoi import QuantityOfInterest

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class SimulationDefinition(object):

    def __init__(self, env_man: EnvironmentManager, par_var: ParameterVariation, qoi: QuantityOfInterest,
                 sc: ScenarioChanges=None):

        self.name = env_man.name
        self.basis_file = env_man.scenario_basis
        self.model = env_man.model
        self.par_var = par_var
        self.qoi = qoi
        self.sc = sc
