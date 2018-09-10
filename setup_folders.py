#!/usr/bin/env python3

import os
import json
import shutil

from paths_and_filenames import *

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


# TODO: at the moment there is a silent full replacement of all files
# TODO think of handling how to do this in future, cannot replace folder with important results
# Option 1: have another folder, indicating the version...?
if True or not os.path.exists(CFG_FOLDER_PATH):
    try:
        shutil.rmtree(CFG_FOLDER_PATH)
    except FileNotFoundError:
        pass

    os.mkdir(CFG_FOLDER_PATH)
    shutil.copytree(os.path.join(SRC_PATH, "models"), MODEL_PATH)

    with open(os.path.join(".", "suqc", "suq_config.json"), "r") as f:
        config_file = json.loads(f.read())

    config_file["container_paths"] = [CON_FOLDER]

    with open(os.path.join(CFG_FOLDER_PATH, "suq_config.json"), "w") as f:
        json.dump(config_file, f, indent=4)

else:
    print(f"INFO: Folder {CFG_FOLDER} already exists. ") # TODO: future: ask user to replace folder -- Caution: may delete content...

if True or not os.path.exists(CON_FOLDER):
    try:
        shutil.rmtree(CON_FOLDER)
    except FileNotFoundError:
        pass
    shutil.copytree(os.path.join(".", "suqc", "envs"), CON_FOLDER)
else:
    print(f"INFO: Folder {CFG_FOLDER_PATH} already exists. ")  # see TODO above