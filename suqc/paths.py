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


PACKAGE_NAME = "suqc"

SUQ_CONFIG_FILE = "suq_config.json"
MODELS_FOLDER = "models"
CFG_PACKAGE_FOLDER = ".suqc"
CON_PACKAGE_FOLDER = "suqc_envs"
CON_LOCAL_FOLDER = "envs"
PACKAGE_FILE = "PACKAGE.txt"

# TODO: make a central file of all the (config-) filenames, set by suq-controller!
# relative path of this file:
SRC_PATH = p.abspath(p.join(p.realpath(__file__), os.pardir, PACKAGE_NAME))
PACKAGE_FILE_PATH = p.join(SRC_PATH, PACKAGE_FILE)

if p.exists(PACKAGE_FILE_PATH):  # Package run
    HOME_PATH = pathlib.Path.home()
    CFG_FOLDER_PATH = p.join(HOME_PATH, CFG_PACKAGE_FOLDER)
    SUQ_CONFIG_PATH = p.join(CFG_FOLDER_PATH, SUQ_CONFIG_FILE)
    MODEL_PATH = p.join(CFG_FOLDER_PATH, MODELS_FOLDER)
    CON_FOLDER = p.join(HOME_PATH, CON_PACKAGE_FOLDER)
else:  # Local run
    CFG_FOLDER_PATH = SRC_PATH
    SUQ_CONFIG_PATH = p.join(SRC_PATH, SUQ_CONFIG_FILE)
    MODEL_PATH = p.join(SRC_PATH, MODELS_FOLDER)
    CON_FOLDER = p.join(SRC_PATH, CON_LOCAL_FOLDER)
