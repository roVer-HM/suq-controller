#!/usr/bin/env python3 

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import os
import subprocess
import glob
import pickle
import abc

import numpy as np

from typing import *

from fabric import Connection

from suqc.configuration import get_suq_config, store_server_config, EnvironmentManager, VadereConsoleWrapper
from suqc.qoi import QuantityOfInterest
from suqc.parameter.create import ParameterVariation
from suqc.parameter.postchanges import ScenarioChanges
from suqc.parameter.sampling import FullGridSampling
from suqc.utils.general import create_folder, check_parent_exists_folder_remove, parent_folder_clean, str_timestamp

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class ServerConnection(object):

    READ_VERSION = "python3 -c 'import suqc; print(suqc.__version__)'"

    def __init__(self):
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


class ServerRequest(object):

    def __init__(self):
        self.server = None
        self.remote_env_name = None
        self.remote_folder_path = None
        self.is_setup = False

    def setup_connection(self, server_connection):
        self.server = server_connection

        # NOTE: do NOT use os.path because the remote is linux, but if local is windows wrong slashes are used
        # NOTE: DO NOT EXPAND TILES "~" AS THIS IS MOSTLY NOT SUPPORTED!

        self.remote_env_name = "_".join(["output", str_timestamp()])

        self.remote_folder_path = self._join_linux_path(["suqc_envs", self.remote_env_name], True)
        self._generate_remote_folder()
        self.is_setup = True

    @classmethod
    def open_arg_pickle(cls, remote_pickle_arg_path):
        with open(remote_pickle_arg_path, "rb") as file:
            kwargs = pickle.load(file)
        return kwargs

    @classmethod
    def dump_result_pickle(cls, res, remote_pickle_res_path):
        with open(os.path.abspath(remote_pickle_res_path), "wb") as file:
            pickle.dump(res, file)

    def _generate_remote_folder(self):
        self.server.con.run(f"mkdir {self.remote_folder_path}")

    def _correct_folderpath(self, p):
        if not p.endswith("/"):
            p = "".join([p, "/"])
        return p

    def _join_linux_path(self, p: list, is_folder: bool):
        lpath = "/".join(p)

        if is_folder:
            lpath = self._correct_folderpath(lpath)

        return lpath

    def _remote_input_folder(self):
        # input data is directly written to the remote folder
        return self.remote_folder_path

    def remote_output_folder(self):
        # TODO: not so clean to reference to EnvironmentManager
        return self._join_linux_path([self.remote_folder_path, EnvironmentManager.output_folder], True)

    def _transfer_local2remote(self, local_filepath):
        remote_target_path = self._join_linux_path([self.remote_folder_path, os.path.basename(local_filepath)], False)
        self.server.con.put(local_filepath, self.remote_folder_path)
        return remote_target_path

    def _compress_output(self):

        compressed_filepath = self._join_linux_path([self.remote_folder_path, "vadere_output.tar.gz"], is_folder=False)

        # from https://stackoverflow.com/questions/939982/how-do-i-tar-a-directory-of-files-and-folders-without-including-the-directory-it
        s = f"""cd {self.remote_output_folder()} && tar -zcvf ../{os.path.basename(compressed_filepath)} . && cd -"""
        self.server.con.run(s)
        return compressed_filepath

    def _transfer_remote2local(self, remote_path, local_path):
        self.server.con.get(remote_path, local_path)

    def _transfer_model_local2remote(self, model):
        model = VadereConsoleWrapper.infer_model(model)
        return self._transfer_local2remote(local_filepath=model.jar_path)

    def _transfer_compressed_output_remote2local(self, local_path):
        target_file = self._compress_output()

        zip_path = parent_folder_clean(local_path)

        filename = os.path.basename(target_file)
        local_filepath = os.path.join(zip_path, filename)
        self._transfer_remote2local(remote_path=target_file, local_path=local_filepath)

        return local_filepath

    def _transfer_pickle_local2remote(self, **kwargs):
        local_pickle_filepath = os.path.join(EnvironmentManager.get_container_path(), "arguments.p")  # TODO: maybe better to add the Timstamp, to not have any clashes!
        with open(local_pickle_filepath, "wb") as file:
            pickle.dump(kwargs, file)

        remote_pickle_path = self._transfer_local2remote(local_pickle_filepath)
        os.remove(local_pickle_filepath)

        return remote_pickle_path

    def _transfer_pickle_remote2local(self, remote_pickle, local_pickle):
        self.server.con.get(remote_pickle, local_pickle)

        with open(local_pickle, "rb") as file:
            res = pickle.load(file)

        os.remove(local_pickle)

        return res

    def _uncompress_file2target(self, local_compressed_file, path_output):

        if not os.path.exists(path_output):
            create_folder(path_output)

        subprocess.call(["tar", "xvzf", local_compressed_file, "-C", path_output])
        subprocess.call(["rm", local_compressed_file])

    def _remove_remote_folder(self):
        s = f"""rm -r {self.remote_folder_path}"""
        self.server.con.run(s)

    @DeprecationWarning
    def provide_single_scenario(self, path_scenario, path_output, model, qoi=None):

        check_parent_exists_folder_remove(path_output, True)

        # Setup
        remote_scenario_location = self._transfer_local2remote(path_scenario)
        remote_model_location = self._transfer_model_local2remote(model)

        if qoi is not None:  # TODO
            raise NotImplementedError(
                "Currently obtaining the qoi is not supported with function 'provide_single_scenario'.")

        # Run remote
        s = f"""python3 -c 'import suqc; suqc.provide_single_scenario(
        path_scenario=\"{remote_scenario_location}\", 
        path_output=\"{self.remote_output_folder()}\", 
        model=\"{remote_model_location}\", qoi=None)'"""

        self.server.con.run(s)

        zipped_file_local = self._transfer_compressed_output_remote2local(path_output)
        self._uncompress_file2target(zipped_file_local, path_output)

        self._remove_remote_folder()

    @DeprecationWarning
    def provide_scenarios_run(self, path_scenarios, path_output, model, njobs: int = 1):

        check_parent_exists_folder_remove(path_output, True)

        path_scenarios = os.path.abspath(path_scenarios)
        assert os.path.isdir(path_scenarios)

        for file in glob.glob(os.path.join(path_scenarios, "*.scenario")):
            self._transfer_local2remote(file)

        remote_model_location = self._transfer_model_local2remote(model)

        # provide_scenarios_run(path_scenarios, path_output, model, njobs: int = 1)

        s = f"""python3 -c 'import suqc; suqc.provide_scenarios_run(
        path_scenarios=\"{self.remote_folder_path}\", 
        path_output=\"{self.remote_output_folder()}\", 
        model=\"{remote_model_location}\", njobs={njobs})'"""

        self.server.con.run(s)

        # TODO: duplicated code!
        zipped_file_local = self._transfer_compressed_output_remote2local(path_output)
        self._uncompress_file2target(zipped_file_local, path_output)
        self._remove_remote_folder()


    @DeprecationWarning
    def single_key_request(self, scenario_path: str, key: str, values: np.ndarray, qoi: Union[str, List[str]],
                       model: str, njobs:int=1):

        remote_scenario_path = self._transfer_local2remote(scenario_path)
        remote_model_path = self._transfer_model_local2remote(model)

        pickle_content = {"sp": remote_scenario_path, "key": key, "val":values, "qoi": qoi, "model": remote_model_path,
                          "njobs": njobs}

        remote_pickle_arg_path = self._transfer_pickle_local2remote(**pickle_content)
        remote_pickle_res_path = self._join_linux_path([self.remote_folder_path, "result.p"], is_folder=False)

        s = f"""python3 -c 'import suqc; from suqc.minimuc import wrapper; wrapper.single_key_request_remote("{remote_pickle_arg_path}", "{remote_pickle_res_path}", "{self.remote_env_name}")'"""
        self.server.con.run(s)

        local_pickle_path = os.path.join(EnvironmentManager.get_container_path(), "result.p")

        res = self._transfer_pickle_remote2local(remote_pickle_res_path, local_pickle_path)

        return res

    def quick_request(self, scenario_path: str, parameter_var: List[dict], qoi: Union[str, List[str]], model: str, njobs:int=1):
        remote_scenario_path = self._transfer_local2remote(scenario_path)
        remote_model_path = self._transfer_model_local2remote(model)

        pickle_content = {"sp": remote_scenario_path, "par_var": parameter_var, "qoi": qoi, "model": remote_model_path, "njobs": njobs}

        # TODO: duplicated code!
        remote_pickle_arg_path = self._transfer_pickle_local2remote(**pickle_content)
        remote_pickle_res_path = self._join_linux_path([self.remote_folder_path, "result.p"], is_folder=False)

        s = f"""python3 -c 'import suqc; from suqc.minimuc import wrapper; wrapper.single_quick_request_remote("{remote_pickle_arg_path}", "{remote_pickle_res_path}", "{self.remote_env_name}")'"""

        self.server.con.run(s)

        local_pickle_path = os.path.join(EnvironmentManager.get_container_path(), "result.p")
        res = self._transfer_pickle_remote2local(remote_pickle_res_path, local_pickle_path)

        self._remove_remote_folder()

        return res

    @DeprecationWarning
    def vary_scenario_run(self, env_man: EnvironmentManager, par_var: ParameterVariation, model: str,
                  qoi: Union[str, List[str], QuantityOfInterest], sc_change: ScenarioChanges = None, njobs: int = 1):

        self._transfer_local2remote(env_man.path_basis_scenario)
        remote_model_path = self._transfer_model_local2remote(model)

        pickle_content = {"par_var": par_var, "qoi": qoi, "model": remote_model_path, "sc_change": sc_change,
                          "njobs": njobs}

        remote_pickle_arg_path = self._transfer_pickle_local2remote(**pickle_content)
        remote_pickle_res_path = self._join_linux_path([self.remote_folder_path, "result.p"], is_folder=False)

        s = f"""python3 -c 'import suqc; from suqc.minimuc import wrapper; wrapper.vary_scenario_run_remote("{remote_pickle_arg_path}", "{remote_pickle_res_path}", "{self.remote_env_name}")'"""

        self.server.con.run(s)

        local_pickle_path = os.path.join(env_man.get_env_outputfolder_path(), "result.p")
        res = self._transfer_pickle_remote2local(remote_pickle_res_path, local_pickle_path)

        self._remove_remote_folder()

        return res

    @classmethod
    @abc.abstractmethod
    def _remote_run(cls, **kwargs):
        raise NotImplementedError("Base class")

    @abc.abstractmethod
    def remote(self, **kwargs):
        raise NotImplementedError("Base class")



if __name__ == "__main__":
    # with ServerConnection() as sc:
    #     ServerRequest(sc).provide_single_scenario(path_scenario="/home/daniel/Code/vadere/VadereModelTests/TestOSM/scenarios/basic_2_density_discrete_ca.scenario",
    #                                               path_output="/home/daniel/scenario_output",
    #                                               model="/home/daniel/Code/suq-controller/suqc/models/vadere0_7rc.jar")

    # with ServerConnection() as sc:
    #     ServerRequest(sc).provide_scenarios_run("/home/daniel/Code/vadere/VadereModelTests/TestOSM/scenarios",
    #                                             path_output="/home/daniel/test/output",
    #                                             model="/home/daniel/Code/suq-controller/suqc/models/vadere0_7rc.jar",
    #                                             njobs=-1)

    # with ServerConnection() as sc:
    #     ServerRequest(sc).single_key_request("/home/daniel/REPOS/vadere/VadereModelTests/TestOSM/scenarios/basic_2_density_discrete_ca.scenario",
    #                                          key="speedDistributionMean", values=np.array([1.0, 1.5]), qoi="density.txt",
    #                                          model="vadere0_7rc.jar", njobs=1)

    # with ServerConnection() as sc:
    #     par_var = [{"speedDistributionMean": 1.0, "maximumSpeed": 3.0},
    #                {"speedDistributionMean": 1.3, "maximumSpeed": 4.0, "acceleration": 3.0}]
    #
    #     res = ServerRequest(sc).quick_request("/home/daniel/REPOS/vadere/VadereModelTests/TestOSM/scenarios/basic_2_density_discrete_ca.scenario",
    #                                           par_var , qoi="density.txt", model="vadere0_7rc.jar", njobs=1)

    with ServerConnection() as sc:

        env_man = EnvironmentManager.create_environment("test_remote",
                                                        basis_scenario="/home/daniel/REPOS/vadere/VadereModelTests/TestOSM/scenarios/basic_2_density_discrete_ca.scenario",
                                                        replace=True)

        par_var = FullGridSampling(grid={"speedDistributionMean": np.array([1., 1.2])})

        res = ServerRequest(sc).vary_scenario_run(env_man=env_man, par_var=par_var, qoi="density.txt", model="vadere0_7rc.jar", njobs=1)

    print(res)