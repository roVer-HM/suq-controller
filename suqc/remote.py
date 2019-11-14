#!/usr/bin/env python3

import abc
import os
import pickle
import zipfile

import numpy as np
import pandas as pd
from fabric import Connection

from suqc.configuration import SuqcConfig
from suqc.utils.general import create_folder, str_timestamp


class ServerConnection(object):

    READ_VERSION_CMD = "python3 -c 'import suqc; print(suqc.__version__)'"

    def __init__(self):
        self._con = None

    @property
    def connection(self):
        if self._con is None:
            raise RuntimeError("Connection is None. Server not initialized.")
        return self._con

    def __enter__(self):
        self._connect_server()
        return self

    def __exit__(self, type, value, traceback):
        self.connection.close()
        print("INFO: Server connection closed.")

    def read_server_config(self):

        server_cfg = SuqcConfig.load_cfg_file()["server"]

        if not server_cfg["host"] or not server_cfg["user"] or server_cfg["port"] <= 0:
            host = input("Enter host name:")
            user = input("Enter user name:")
            port = int(input("Enter port number (int):"))
            SuqcConfig.store_server_config(host, user, port)
            server_cfg = SuqcConfig.load_cfg_file()["server"]
        else:
            host, user, port = server_cfg["host"], server_cfg["user"], server_cfg["port"]
        print(f"INFO: Trying to connect to ssh -p {port} {user}@{host} . "
              f"Configure at {SuqcConfig.path_suq_config_file()}")
        return server_cfg

    def _connect_server(self):

        server_cfg = self.read_server_config()

        self._con: Connection = Connection(server_cfg["host"],
                                           user=server_cfg["user"],
                                           port=server_cfg["port"],
                                           config=None)

        version = self.read_terminal_stdout(ServerConnection.READ_VERSION_CMD)
        print(f"INFO: Connection established. Detected suqc version {version} on server "
              f"({server_cfg['host']}:{server_cfg['port']}) side.")
        print(f"INFO: pandas=={pd.__version__} and numpy=={np.__version__} on server.")

    def read_terminal_stdout(self, s: str) -> str:
        r = self._con.run(s)
        return r.stdout.rstrip()  # rstrip -> remove trailing whitespaces and new lines


class ServerRequest(object):

    zip_filename = "output.zip"

    def __init__(self):
        self.server = None
        self.remote_env_name = None
        self.remote_folder_path = None
        self.is_setup = False

    def setup_environment(self, server_connection):
        self.server = server_connection

        # NOTE: do NOT use os.path because the remote is linux, but if local is windows wrong slashes are used
        # NOTE: do NOT epxand tiles "~" as this is mostly not supported!

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
        self.server.connection.run(f"mkdir {self.remote_folder_path}")

    def _correct_folderpath(self, p):
        if not p.endswith("/"):
            p = "".join([p, "/"])
        return p

    def _join_linux_path(self, p: list, is_folder: bool):
        lpath = "/".join(p)

        if is_folder:
            lpath = self._correct_folderpath(lpath)

        return lpath

    def _default_result_pickle_path_remote(self):
        return self._join_linux_path([self.remote_folder_path, "result.p"], is_folder=False)

    def _default_argument_pickle_path_remote(self):
        return self._join_linux_path([self.remote_folder_path, "arguments.p"], is_folder=False)

    def _default_result_pickle_path_local(self, suitable_path):
        return os.path.join(suitable_path, "result.p")

    def _remote_input_folder(self):
        # input data is directly written to the remote folder
        return self.remote_folder_path

    def _transfer_local2remote(self, local_filepath, remove_local_file=False):
        remote_target_path = self._join_linux_path([self.remote_folder_path, os.path.basename(local_filepath)], False)
        self.server.connection.put(local_filepath, self.remote_folder_path)

        if remove_local_file:
            os.remove(local_filepath)

        return remote_target_path

    def _compress_output(self):
        compressed_filepath = self._join_linux_path([self.remote_folder_path, self.zip_filename], is_folder=False)
        s = f"""python3 -c 'import suqc; suqc.ServerRequest.zip_environment("{self.remote_folder_path}") '"""
        self.server.connection.run(s)
        return compressed_filepath

    def _transfer_remote2local(self, remote_path, local_path):
        self.server.connection.get(remote_path, local_path)

    def _transfer_compressed_output_remote2local(self, local_path):
        target_file = self._compress_output()

        filename = os.path.basename(target_file)
        local_filepath = os.path.join(local_path, filename)
        self._transfer_remote2local(remote_path=target_file, local_path=local_filepath)
        return local_filepath

    def _transfer_pickle_local2remote(self, pickle_content):
        local_pickle_filepath = os.path.join(SuqcConfig.path_container_folder(), "arguments.p")
        with open(local_pickle_filepath, "wb") as file:
            pickle.dump(pickle_content, file)

        remote_pickle_path = self._transfer_local2remote(local_pickle_filepath)
        os.remove(local_pickle_filepath)

        assert remote_pickle_path == self._default_argument_pickle_path_remote()
        return remote_pickle_path

    def _transfer_pickle_remote2local(self, remote_pickle, local_pickle):
        self.server.connection.get(remote_pickle, local_pickle)

        with open(local_pickle, "rb") as file:
            res = pickle.load(file)
        os.remove(local_pickle)
        return res

    def _uncompress_file2target(self, local_compressed_file, path_output):

        if not os.path.exists(path_output):
            create_folder(path_output)

        with zipfile.ZipFile(local_compressed_file, "r") as result_zip:
            result_zip.extractall(path=path_output)

        os.remove(local_compressed_file)

    def _remove_remote_folder(self):
        s = f"""rm -r {self.remote_folder_path}"""
        self.server.connection.run(s)

    @staticmethod
    def _add_directory(dir_path, zipobj, prefix=""):

        full_arc_dir = ""

        for folder_name, subfolders, filenames in os.walk(dir_path):
            arcdir = os.path.join(prefix, os.path.basename(folder_name))
            full_arc_dir = os.path.join(full_arc_dir, arcdir)
            for filename in filenames:
                # create complete filepath of file in directory
                filepath = os.path.join(folder_name, filename)
                # Add file to zip
                zipobj.write(filepath, arcname=os.path.join(full_arc_dir, filename))

    @staticmethod
    def zip_environment(env_path):

        zip_path = os.path.join(env_path, ServerRequest.zip_filename)
        zipobj = zipfile.ZipFile(zip_path, 'w')

        exclude_file_endings = ["p", "jar", "zip"]  # pickle and jar files are excluded

        for filename in os.listdir(env_path):
            filepath = os.path.join(env_path, filename)

            if os.path.isdir(filepath):
                ServerRequest._add_directory(filepath, zipobj)
            else:
                file_ending = filename.split(".")[-1]
                if file_ending not in exclude_file_endings:
                    zipobj.write(filepath, arcname=filename)
        zipobj.close()

    @classmethod
    @abc.abstractmethod
    def _remote_run(cls, remote_pickle_arg_path):
        raise NotImplementedError("Base class")

    def _attach_pickle_file_with_paths(self,
                                       local_pickle_content,
                                       local_model_obj,
                                       remote_pickle_arg_path,
                                       remote_pickle_res_path,
                                       remote_env_name,
                                       remote_model_path):

        local_pickle_content["model"] = local_model_obj
        local_pickle_content["remote_pickle_arg_path"] = remote_pickle_arg_path
        local_pickle_content["remote_pickle_res_path"] = remote_pickle_res_path
        local_pickle_content["remote_env_name"] = remote_env_name
        local_pickle_content["remote_folder_path"] = self.remote_folder_path
        local_pickle_content["remote_model_path"] = remote_model_path
        return local_pickle_content

    def _remote_ssh_logic(self,
                          local_env_man,
                          local_pickle_content,
                          local_transfer_files,
                          local_model_obj,
                          class_name,
                          transfer_output):

        with ServerConnection() as sc:
            self.setup_environment(sc)

            # put model_path in list of files to transfer:
            remote_model_path = self._transfer_local2remote(local_model_obj)
            local_model_obj.jar_file = remote_model_path  # update the path for the remote server

            for key, filepath in local_transfer_files.items():
                assert os.path.exists(filepath)
                local_pickle_content[key] = self._transfer_local2remote(filepath)

            remote_pickle_arg_path = self._default_argument_pickle_path_remote()
            remote_pickle_res_path = self._default_result_pickle_path_remote()

            local_pickle_content = self._attach_pickle_file_with_paths(local_pickle_content=local_pickle_content,
                                                                       local_model_obj=local_model_obj,
                                                                       remote_pickle_arg_path=remote_pickle_arg_path,
                                                                       remote_pickle_res_path=remote_pickle_res_path,
                                                                       remote_env_name=self.remote_env_name,
                                                                       remote_model_path=remote_model_path)

            self._transfer_pickle_local2remote(local_pickle_content)

            s = f"""python3 -c 'import suqc; suqc.{class_name}._remote_run("{remote_pickle_arg_path}")'"""
            self.server.connection.run(s)

            # transfer_result
            local_pickle_path = self._default_result_pickle_path_local(local_env_man.env_path)
            remote_result = self._transfer_pickle_remote2local(remote_pickle_res_path, local_pickle_path)

            self._transfer_pickle_remote2local(remote_pickle_res_path,
                                               self._default_result_pickle_path_local(local_env_man.env_path))

            if transfer_output:
                zipped_file_local = self._transfer_compressed_output_remote2local(local_env_man.env_path)
                self._uncompress_file2target(zipped_file_local, local_env_man.env_path)

            self._remove_remote_folder()
            return remote_result

if __name__ == "__main__":
    ServerRequest.zip_environment("/home/daniel/Code/suq-controller/tutorial/example_output")
