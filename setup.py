#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

from setuptools import setup, find_packages

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------

import os
import json
import pathlib
import shutil

# TODO: rename back to try_outs
# TODO: create and fill the 2 standard folders ".suqc" (models and configuration) and "suqc_container" (environments, put in the environments, that are in the repo)
# TODO: --> need to create the appropriate JSON default

HOME_PATH = pathlib.Path.home()
CFG_FOLDER = os.path.join(HOME_PATH, ".suqc")
MODEL_FOLDER = os.path.join(CFG_FOLDER, "models")

CON_FOLDER = os.path.join(HOME_PATH, "suqc_envs")

PACKAGE_FILE = os.path.join(".", "suqc", "PACKAGE.txt")

VERSION = "0.1"
with open(PACKAGE_FILE, "w") as file:
    file.write(f"version={VERSION}")

# create file inside the package-> this is an indicator to check between package and local running version
with open(os.path.join(".", "suqc", "PACKAGE.txt"), "w") as file:
    file.write(f"version={VERSION}")

setup(  # TODO include the Package file into the installation!
    name="suqc",
    version=VERSION,
    packages=find_packages(),
    data_files=[('suqc', ["suqc/PACKAGE.txt"])]
)

# create file inside the package-> this is an indicator to check between package and local running version
os.remove(os.path.join(".", "suqc", "PACKAGE.txt"))

if True or not os.path.exists(CFG_FOLDER):  # TODO: at the moment there is a silent full replacement of all files
    shutil.rmtree(CFG_FOLDER)
    os.mkdir(CFG_FOLDER)

    #os.mkdir(MODEL_FOLDER)
    shutil.copytree(os.path.join(".", "suqc", "models"), MODEL_FOLDER)

    with open(os.path.join(".", "suqc", "suq_config.json"), "r") as f:
        config_file = json.loads(f.read())

    config_file["container_paths"] = [CON_FOLDER]

    with open(os.path.join(CFG_FOLDER, "suq_config.json"), "w") as f:
        json.dump(config_file, f, indent=4)

else:
    print(f"INFO: Folder {CFG_FOLDER} already exists. ") # TODO: future: ask user to replace folder -- Caution: may delete content...

if True or not os.path.exists(CON_FOLDER):
    shutil.rmtree(CON_FOLDER)
    shutil.copytree(os.path.join(".", "suqc", "envs"), CON_FOLDER)
else:
    print(f"INFO: Folder {CFG_FOLDER} already exists. ")  # see TODO above

