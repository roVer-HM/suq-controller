#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import os
import json

from try_outs.utils.general import user_query_yes_no

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


# relative path of this file:
SRC_PATH = os.path.relpath(os.path.join(__file__, os.pardir))
SUQ_CONFIG_PATH = os.path.join(SRC_PATH, "suq_config.json")

# configuration of the suq-controller
DEFAULT_SUQ_CONFIG = {"scenario_paths": [os.path.join(SRC_PATH, "scenarios")],
                      "models": dict()}

# configuration saved with each scenario
DEFAULT_SC_CONFIG = {"model": None}


def _convert_to_json(s):
    return json.loads(s)


def _store_json(d):
    with open(SUQ_CONFIG_PATH, "w") as outfile:
        json.dump(d, outfile, indent=4)


def get_suq_config(reset_default=False):
    if reset_default or not os.path.exists(SUQ_CONFIG_PATH):
        with open(SUQ_CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_SUQ_CONFIG, f, indent=4)
        print(f"INFO: Writing default configuration to \n {SUQ_CONFIG_PATH} \n")
        return DEFAULT_SUQ_CONFIG
    else:
        with open(SUQ_CONFIG_PATH, "r") as f:
            config_file = f.read()
        return _convert_to_json(config_file)


def get_model_location(name):
    config = get_suq_config()
    return config["models"][name]


def set_new_model(name, location):
    config = get_suq_config()

    if name in config["models"]:

        if os.path.abspath(location) == os.path.abspath(config["models"][name]):
            return  # is anyway the same path

        if not user_query_yes_no(question=f"The name '{name}' already exists in the lookup table. Do you want to "
                                          f"update the path? \n "
                                          f"{config['models'][name]} --> {location}"):
            return  # not updating the path

    assert os.path.exists(location), f"The location {os.path.abspath(location)} is does not exist."

    config["models"][name] = location
    _store_json(config)

def get_model_names():
    config = get_suq_config()
    return config["models"].keys()


def set_new_scenario_path(p):
    config = get_suq_config()
    assert p not in config["scenario_paths"]
    config["scenario_paths"].append(p)
    _store_json(config)


def remove_scenario_path(p):
    config = get_suq_config()
    config["scenario_paths"].remove(p)


def list_scenario_paths():
    print(get_suq_config()["scenario_paths"])


if __name__ == "__main__":
    get_suq_config(reset_default=False)
    set_new_model("vadere", "./models/vadere-console1.jar")
    print(get_suq_config())

