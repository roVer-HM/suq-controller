#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import pickle
import os
import pandas as pd

from fabric import Connection

from suqc.parameter.sampling import ParameterVariation, FullGridSampling, BoxSampling, RandomSampling
from suqc.parameter.postchanges import ScenarioChanges
from suqc.qoi import QoIProcessor
from suqc.configuration import EnvironmentManager, get_suq_config, store_server_config
from suqc.server.simdef import SimulationDefinition

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


# TODO: if serfer configs are not set yet, then have a routine to ask the user
class ServerConnection(object):

    READ_VERSION = "python3 -c 'import suqc; print(suqc.__version__)'"

    def __init__(self, sudo=False):
        self._sudo = sudo
        self._con = None

    @property
    def con(self):
        if self._con is None:
            raise RuntimeError("Server not initialized.")
        return self._con

    def __enter__(self):
        self._connect_server()
        return self

    def __exit__(self, type, value, traceback):
        self.con.close()
        print("INFO: Server connection closed.")

    def get_server_config(self):
        server_cfg = get_suq_config()["server"]
        if not server_cfg["host"] or not server_cfg["user"] or server_cfg["port"] <= 0:
            host = input("Enter the host server name:")
            user = input("Enter the user name:")
            port = int(input("Enter the port number (int):"))
            store_server_config(host, user, port)
        else:
            host, user, port = server_cfg["host"], server_cfg["user"], server_cfg["port"]
        print(f"INFO: Try to connect to ssh -p {port} {user}@{host} ")
        return server_cfg

    def _connect_server(self):
        #import getpass  # TODO: does not work reall with sudo
        #if self._sudo:
        #     from fabric import Config
        #     sudo_pass = getpass.unix_getpass("What's your sudo password?")
        #     config = Config(overrides={'sudo': {'password': sudo_pass}})
        #else:
        config = None
        server_cfg = self.get_server_config()

        self._con: Connection = Connection(server_cfg["host"],
                                           user=server_cfg["user"],
                                           port=server_cfg["port"],
                                           config=config)

        version = self.read_terminal_stdout(ServerConnection.READ_VERSION)
        print(f"INFO: Connection established. Detected suqc version {version} on server side.")

    @NotImplementedError  # TODO: still problems with sudo with local <-> remote...
    def remove_folder(self, rem_folder, use_sudo=False):
        if use_sudo:
            self.con.sudo(f"rm -r {rem_folder}")
        else:
            self.con.run(f"rm -r {rem_folder}")

    def read_terminal_stdout(self, s: str) -> str:
        r = self._con.run(s)
        return r.stdout.rstrip()  # rstrip -> remove trailing whitespaces and new lines


class ServerSimulation(object):

    FILENAME_PICKLE_SIMDEF = "simdef.p"
    FILENAME_PICKLE_RESULTS = "parameter_results.p"
    FILENAME_PICKLE_PARAMETER = "par_lookup.p"

    def __init__(self, server: ServerConnection):
        self._server = server

    @classmethod
    def _remote_load_simdef(cls, fp):
        with open(fp, "rb") as f:
            simdef = pickle.load(f)
        return simdef

    @classmethod
    def _create_remote_environment(cls, fp):
        from suqc.configuration import remove_environment, create_environment

        simdef = ServerSimulation._remote_load_simdef(fp)
        remove_environment(simdef.name, force=True)  # TODO: for now it is simply gets replaced (a user may loose data)
        create_environment(simdef.name, simdef.basis_file, simdef.model, replace=True)

    @classmethod
    def store_pickle_results(cls, path, par_lookup, results):
        path_parlu = os.path.join(path, ServerSimulation.FILENAME_PICKLE_PARAMETER)
        par_lookup.to_pickle(path_parlu)

        path_results = os.path.join(path, ServerSimulation.FILENAME_PICKLE_RESULTS)
        results.to_pickle(path_results)

        print(path)  # this print statement gets read from console, to have it correctly via scp


    @classmethod
    def _remote_run_env(cls, fp):
        import suqc.query
        import suqc.configuration

        simdef = ServerSimulation._remote_load_simdef(fp)
        env_man = suqc.configuration.EnvironmentManager(simdef.name)

        # njobs = -1 --> always use all available processors as this is the main reason to use the server
        par, res = suqc.query.Query(env_man, simdef.par_var, simdef.qoi, simdef.sc).run(njobs=-1)
        ServerSimulation.store_pickle_results(env_man.env_path, par, res)

    @classmethod
    def remote_simulate(cls, fp):
        ServerSimulation._create_remote_environment(fp)
        ServerSimulation._remote_run_env(fp)

    def _setup_server_env(self, local_pickle_path, simdef):
        with open(local_pickle_path, "wb") as f:
            pickle.dump(simdef, f)

        rem_con_path = self._server.read_terminal_stdout(
            "python3 -c 'import suqc.configuration as c; print(c.get_container_path())'")

        self._server.con.put(local_pickle_path, rem_con_path)

        return os.path.join(rem_con_path, ServerSimulation.FILENAME_PICKLE_SIMDEF)

    def _local_submit_request(self, fp):
        s = f"""python3 -c 'import suqc.server.remote as rem; rem.ServerSimulation.remote_simulate(\"{fp}\")' """
        result = self._server.con.run(s)
        last_line = result.stdout.rstrip().split("\n")[-1]  # last line to get the last 'print(path)' statement
        return last_line

    def _read_results(self, local_path, remote_path):

        self._server.con.get(os.path.join(remote_path, ServerSimulation.FILENAME_PICKLE_PARAMETER),
                             os.path.join(local_path, ServerSimulation.FILENAME_PICKLE_PARAMETER))

        with open(os.path.join(local_path, ServerSimulation.FILENAME_PICKLE_PARAMETER), "rb") as f:
            df_par = pickle.load(f)
            isinstance(df_par, pd.DataFrame)

        self._server.con.get(os.path.join(remote_path, ServerSimulation.FILENAME_PICKLE_RESULTS),
                             os.path.join(local_path, ServerSimulation.FILENAME_PICKLE_RESULTS))

        with open(os.path.join(local_path, ServerSimulation.FILENAME_PICKLE_RESULTS), "rb") as f:
            df_res = pickle.load(f)
            isinstance(df_res, pd.DataFrame)
        return df_par, df_res

    def run(self, env_man: EnvironmentManager, par_var: ParameterVariation, qoi: QoIProcessor,
            sc: ScenarioChanges=None):

        simdef = SimulationDefinition(env_man, par_var, qoi, sc)

        local_pickle_path = os.path.join(env_man.env_path, ServerSimulation.FILENAME_PICKLE_SIMDEF)
        fp_rem_simdef = self._setup_server_env(local_pickle_path=local_pickle_path, simdef=simdef)

        fp_rem_results = self._local_submit_request(fp_rem_simdef)
        fp_loc_results = env_man.env_path

        results = self._read_results(fp_loc_results, fp_rem_results)

        return results


if __name__ == "__main__":
    from suqc.qoi import PedestrianEvacuationTimeProcessor

    env_man = EnvironmentManager("corner")
    par_var = FullGridSampling()
    par_var.add_dict_grid({"speedDistributionStandardDeviation": [0.0]})
    qoi = PedestrianEvacuationTimeProcessor(env_man)

    with ServerConnection() as sc:
        server_sim = ServerSimulation(sc)
        result = server_sim.run(env_man, par_var, qoi)

    print(result)

    # TODO Next steps:
    # TODO: Make a script to update the suqc automatically (fresh installation) --> problems with sudo and ssh
    # TODO: Check how to disable logging in Vadere
