#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import os
import os.path as p
import pathlib

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class Paths(object):

    NAME_PACKAGE = "suqc"
    NAME_SUQ_CONFIG_FILE = "suq_config.json"
    NAME_MODELS_FOLDER = "models"
    NAME_CON_FOLDER = "suqc_envs"
    NAME_PACKAGE_FILE = "PACKAGE.txt"

    IS_PACKAGE: bool = None

    @classmethod
    def is_package_paths(cls):
        if cls.IS_PACKAGE is None:
            return os.path.exists(cls.path_package_indicator_file)
        else:
            return Paths.IS_PACKAGE

    @classmethod
    def set_package_paths(cls, package: bool):
        Paths.IS_PACKAGE = package

    @classmethod
    def _name_cfg_folder(cls):
        if cls.is_package_paths():
            return ".suqc"
        else:
            raise RuntimeError("This should not be called when IS_PACKAGE=False.")

    @classmethod
    def path_usrhome_folder(cls):
        return pathlib.Path.home()

    @classmethod
    def path_src_folder(cls):
        return p.abspath(p.join(p.realpath(__file__), os.pardir))

    @classmethod
    def path_package_indicator_file(cls):
        return p.join(cls.path_src_folder(), cls.NAME_PACKAGE_FILE)

    @classmethod
    def path_cfg_folder(cls):
        if cls.is_package_paths():
            return p.join(cls.path_usrhome_folder(), cls._name_cfg_folder())
        else:
            return cls.path_src_folder()

    @classmethod
    def path_suq_config_file(cls):
        if cls.is_package_paths():
            return p.join(cls.path_cfg_folder(), cls.NAME_SUQ_CONFIG_FILE)
        else:
            return p.join(cls.path_src_folder(), cls.NAME_SUQ_CONFIG_FILE)

    @classmethod
    def path_models_folder(cls):
        if cls.is_package_paths():
            return p.join(cls.path_cfg_folder(), cls.NAME_MODELS_FOLDER)
        else:
            return p.join(cls.path_src_folder(), cls.NAME_MODELS_FOLDER)

    @classmethod
    def path_container_folder(cls):
        if cls.is_package_paths():
            return p.join(cls.path_usrhome_folder(), cls.NAME_CON_FOLDER)
        else:
            return p.join(cls.path_src_folder(), cls.NAME_CON_FOLDER)

if __name__ == "__main__":
    Paths()

