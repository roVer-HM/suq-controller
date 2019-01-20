#!/usr/bin/env python3

import os
import json
import shutil

from suqc.paths import Paths as pa

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


# TODO: at the moment there is a silent full replacement of all files
# TODO think of handling how to do this in future, cannot replace folder with important results
# Option 1: have another folder, indicating the version...?
# TODO: ask for Vadere src path and minimuc server config (make both values (the config file should be ignored!, so that changes are not tracked)


pa.set_package_paths(True)

if True:  # TODO: later on make strategy if folder already exist...
    try:
        shutil.rmtree(pa.path_cfg_folder())
    except FileNotFoundError:
        pass

    os.mkdir(pa.path_cfg_folder())
    shutil.copytree(os.path.join(pa.path_src_folder(), "models"), pa.path_models_folder())

    with open(os.path.join(".", "suqc", "suq_config.json"), "r") as f:
        config_file = json.loads(f.read())

    config_file["container_paths"] = pa.path_container_folder()

    with open(os.path.join(pa.path_cfg_folder(), "suq_config.json"), "w") as f:
        json.dump(config_file, f, indent=4)

else:
    print(f"INFO: Folder {pa.path_cfg_folder()} already exists. ") # TODO: future: ask user to replace folder -- Caution: may delete content...

if True:
    try:
        shutil.rmtree(pa.path_container_folder())
    except FileNotFoundError:
        pass
    shutil.copytree(os.path.join(".", pa.NAME_PACKAGE, pa.NAME_CON_FOLDER), pa.path_container_folder())
else:
    print(f"INFO: Folder {pa.path_container_folder()} already exists. ")  # see TODO above
