#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import pickle
import os
import pandas as pd

from fabric import Connection

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
        self.name = env_man.name
        self.basis_file = env_man.get_vadere_scenario_basis_file()
        self.model = env_man.get_cfg_value("model")
        self.par_var = par_var
        self.qoi = qoi




# TODO: possiby overwrite the context manager ("with"-statement), to automatically close the connection
# http://preshing.com/20110920/the-python-with-statement-by-example/
class ServerConnection(object):

    READ_VERSION = "python3 -c 'import suqc; print(suqc.__version__)'"
    READ_CONPATH = "python3 -c 'import suqc.configuration as c; print(c._get_con_path())'"

    def __init__(self, env_manager: EnvironmentManager, par_var: ParameterVariation, qoi: QoIProcessor):
        self._envman = env_manager
        self._par_var = par_var
        self._qoi = qoi

        self._con = None

    def _connect_server(self):
        self._con: Connection = Connection("minimuc.cs.hm.edu", user="dlehmberg", port=5022)
        version = self.read_terminal_stdout(ServerConnection.READ_VERSION)
        print(f"INFO: Connection established. Setected suqc version {version} on server side.")

    def read_terminal_stdout(self, s: str) -> str:
        r = self._con.run(s)
        return r.stdout.rstrip()  # rstrip -> remove trailing whitespaces and new lines

    def _send_file2server(self, local_fp, server_fp):
        self._con.put(local_fp, server_fp)

    def create_pickle(self):


    def send_pickle2server(self):
        # TODO: local path
        pickle_path = "INVALID"

        rconpath = self.read_terminal_stdout(ServerConnection.READ_CONPATH)
        renvpath = os.path.join(rconpath, self._envman.name)
        self._send_file2server(pickle_path, renvpath)



class ServerSimulation(object):

    def __init__(self, server: ServerConnection, env_man: EnvironmentManager):
        self._server = server
        self._env_man = env_man




    @classmethod
    def _create_remote_environment(cls, fp):
        from suqc.configuration import create_environment
        simdef = pickle.load(fp)
        create_environment(simdef.name, simdef.basis_file, simdef.model, replace=True)

    @classmethod
    def _remote_run_env(cls, fp):
        import suqc.query
        import suqc.configuration
        simdef = pickle.load(fp)

        env_man = suqc.configuration.EnvironmentManager(simdef.name)
        ret = suqc.query.Query(env_man, simdef.qoi).query_simulate_all_new(simdef.par_var, njobs=-1)
        path = "INVALID"  # TODO
        ret.to_pickle(path)
        print(path)

    @classmethod
    def remote_simulate(cls, fp):
        ServerSimulation._create_remote_environment(fp)
        ServerSimulation._remote_run_env(fp)

    def _setup_server_env(self):
        simdef = SimulationDefinition(self._envman, self._par_var, self._qoi)

        with open("TODO:path", "wb") as f:
            pickle.dump(simdef, f)


    def _local_submit_request(self):
        s = f"""python3 -c 'import suqc.rem; rem.ServerProcedure.simulate_remote({self._rem_simdef_fp})'"""
        result = self._con.run(s)
        last_line = result.stdout.rstrip().split("\n")[-1]  # last line to get the last 'print(path)' statement
        return last_line

    def _read_results(self, local_path, remote_path):
        self._con.get(remote_path, local_path)

        with open(local_path, "rb") as f:
            df = pickle.load(f)
            isinstance(df, pd.DataFrame)
        return df

    def run(self):  # TODO: need to get the local path, where to save the pickle...
        self._setup_server_env()
        fp_results = self._local_submit_request()
        results = self._read_results("INVALID", fp_results)
        return results

