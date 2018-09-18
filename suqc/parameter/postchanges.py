#!/usr/bin/env python3 

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import abc

from suqc.utils.dict_utils import change_existing_dict

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class ScenarioChanges(object):

    def __init__(self):
        self._apply_scenario_changes = {}
        self._defaults()

    def _defaults(self):
        self.add_scenario_change(ChangeRandomNumber())

    def add_scenario_change(self, sc: 'PostScenarioChange'):
        # ABCScenarioChange in '' to support forward reference,
        # see https://www.python.org/dev/peps/pep-0484/#forward-references
        if sc.name in self._apply_scenario_changes.keys():
            raise KeyError(f"Scenario change with {sc.name} is already present.")
        self._apply_scenario_changes[sc.name] = sc

    def _collect_changes(self, par_id, scenario):
        changes = {}
        for chn in self._apply_scenario_changes.values():
            changes.update(chn.get_changes_dict(par_id, scenario))
        return changes

    def change_scenario(self, par_id, scenario):
        return change_existing_dict(scenario, changes=self._collect_changes(par_id, scenario))


class PostScenarioChange(metaclass=abc.ABCMeta):

    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def get_changes_dict(self, par_id, scenario, par_var_changes):
        raise NotImplementedError("ABC method")


class ChangeRandomNumber(PostScenarioChange):
    KEY_FIXED = "useFixedSeed"
    KEY_SEED = "fixedSeed"

    def __init__(self):
        super(ChangeRandomNumber, self).__init__(name="random_number")

    def get_changes_dict(self, par_id, scenario, par_var_changes):
        # TODO: Currently the seed in VADERE is set to the par_id -- this may not always be desired...
        # 4294967295 = max unisgned 32 bit integer
        return {ChangeRandomNumber.KEY_FIXED: True, ChangeRandomNumber.KEY_SEED: par_id}


class ChangeScenarioName(PostScenarioChange):

    KEY_NAME = "name"

    def __init__(self):
        super(ChangeScenarioName, self).__init__(name="scenario_name")

    def get_changes_dict(self, par_id, scenario, par_var_changes):
        existing = scenario[ChangeScenarioName.KEY_NAME]
        return {ChangeScenarioName.KEY_NAME: "_".join([existing, str(par_id)])}


class ChangeDescription(PostScenarioChange):

    KEY_DESCRIPTION = "description"

    def __init__(self):
        super(ChangeDescription, self).__init__(name="description")
    
    def get_changes_dict(self, par_id, scenario, par_var_changes):
        return {ChangeDescription.KEY_DESCRIPTION: " ".join([f"par_id={par_id}", str(par_var_changes)])}