#!/usr/bin/env python3 

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

# include imports after here:
import os
import json

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


# path of this file:
SRC_PATH = os.path.abspath(os.path.join(__file__, os.pardir))

SUQ_CONFIG_PATH = os.path.join(SRC_PATH, "suq_config.json")

# configuration of the suq-controller


DEFAULT_SUQ_CONFIG = f"""{{
"scenario_paths": ["{os.path.join(SRC_PATH, "scenarios")}"],
"models": 
{{
}}

}}"""


# configuration saved with each scenario
DEFAULT_SC_CONFIG = f"""{{
"model": null
}}"""


def _convert_to_json(s):
    return json.loads(s)


def _store_json(d):
    json.dump(d, SUQ_CONFIG_PATH)


def get_suq_config(set_default=False):
    if set_default or not os.path.exists(SUQ_CONFIG_PATH):
        with open(SUQ_CONFIG_PATH, "w") as f:
            f.write(DEFAULT_SUQ_CONFIG)
        print(f"INFO: Writing default configuration to \n {SUQ_CONFIG_PATH} \n")
        return _convert_to_json(DEFAULT_SUQ_CONFIG)
    else:
        with open(SUQ_CONFIG_PATH, "r") as f:
            config_file = f.read()
        return _convert_to_json(config_file)


def get_model_location(name):
    config = get_suq_config()
    return config["models"][name]


def set_new_model(name, location):
    config = get_suq_config()
    assert name not in config["models"]
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

    pass