#!/usr/bin/env python3 

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import pickle

from suqc.parameter import ParameterVariation
from suqc.qoi import QoIProcessor
from suqc.configuration import EnvironmentManager

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class SimulationDefinition(object):

    def __init__(self, env_man: EnvironmentManager, par_var: ParameterVariation, qoi: QoIProcessor):
        self.basis_file = env_man.get_vadere_scenario_basis_file()
        self.sim_cfg = env_man.get_cfg_file()
        self.par_var = par_var
        self.qoi = qoi


class ServerProcedure(object):

    def __init__(self, pickle_filepath):
        pass

    def create_environment(self):
        pass

    def run_environment(self):
        pass  # store result as pickle  # its important to write the error in a file to have


class ServerSimulation(object):

    def __init__(self, env_manager: EnvironmentManager, par_var: ParameterVariation, qoi: QoIProcessor):
        self._envman = env_manager
        self._par_var = par_var
        self._qoi = qoi


    def create_pickle(self):
        simdef = SimulationDefinition(self._envman, self._par_var, self._qoi)

        with open("TODO:path", "wb") as f:
            pickle.dump(simdef, f)

    def send_pickle2server(self):
        pass

    def run_simulation_on_server(self):
        pass

    def read_results(self):
        pass







def _create_environment(pickle_filepath):
    # create an environment
    # remove existing environments with 'name'
    pass


def run_pickled_environment(pickle_filepath):
    _create_environment(pickle_filepath)


