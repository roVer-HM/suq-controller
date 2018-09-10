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

NAME_PACKAGE = "suqc"

NAME_SUQ_CONFIG_FILE = "suq_config.json"
NAME_MODELS_FOLDER = "models"
NAME_CON_FOLDER = "suqc_envs"

NAME_PACKAGE_FILE = "PACKAGE.txt"

# TODO: make a central file of all the (config-) filenames, set by suq-controller!
# relative path of this file:
PATH_SRC = p.abspath(p.join(p.realpath(__file__), os.pardir, NAME_PACKAGE))
PATH_PACKAGE_FILE = p.join(PATH_SRC, NAME_PACKAGE_FILE)

if p.exists(PATH_PACKAGE_FILE):  # Package run
    NAME_CFG_FOLDER = ".suqc"

    PATH_HOME = pathlib.Path.home()
    PATH_CFG_FOLDER = p.join(PATH_HOME, NAME_CFG_FOLDER)
    PATH_SUQ_CONFIG = p.join(PATH_CFG_FOLDER, NAME_SUQ_CONFIG_FILE)
    PATH_MODELS = p.join(PATH_CFG_FOLDER, NAME_MODELS_FOLDER)
    PATH_CONTAINER = p.join(PATH_HOME, NAME_CON_FOLDER)
else:  # Local run
    NAME_CFG_FOLDER = "suqc"

    PATH_CFG_FOLDER = PATH_SRC
    PATH_SUQ_CONFIG = p.join(PATH_SRC, NAME_SUQ_CONFIG_FILE)
    PATH_MODELS = p.join(PATH_SRC, NAME_MODELS_FOLDER)
    PATH_CONTAINER = p.join(PATH_SRC, NAME_CON_FOLDER)
