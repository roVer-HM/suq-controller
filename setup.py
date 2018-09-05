#!/usr/bin/env python3 

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

from setuptools import setup

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------

import os
import pathlib
import shutil

# TODO: rename back to try_outs
# TODO: create and fill the 2 standard folders ".suqc" (models and configuration) and "suqc_container" (environments, put in the environments, that are in the repo)
# TODO: --> need to create the appropriate JSON default

os.rename("./try_outs", "suqc")  # TODO: remove when final package name

setup(
    name="suqc",
    version="0.01"
)

HOME_PATH = pathlib.Path.home()
CFG_FOLDER = os.path.join(HOME_PATH, ".suqc")
CON_FOLDER = os.path.join(HOME_PATH, "suqc_envs")

# check if folder already exists

if not os.path.exists(CFG_FOLDER):
    os.mkdir(CFG_FOLDER)

    with open("./suqc/suq_config.json", "r") as f:
        config_file = json.loads(f.read())

    config_file["container_paths"] = [CON_FOLDER]

    with open(SUQ_CONFIG_PATH, "w") as f:
        json.dump(DEFAULT_SUQ_CONFIG, f, indent=4)




else:
    print(f"INFO: Folder {CFG_FOLDER} already exists. ") # TODO: future: ask user to replace folder -- Caution: may delete content...



if not os.path.exists(ENV_FOLDER):
    os.mkdir(CON_FOLDER)
else:
    print(f"INFO: Folder {CFG_FOLDER} already exists. ")  # see TODO above







shutil.copyfile(, os.path.join(CFG_FOLDER, "suq_config.json"))

# TODO: create an empty file inside the package with name "package" -> this is an indicator to check between package and local running


