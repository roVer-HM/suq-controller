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


class PostVariation(metaclass=abc.ABCMeta):

    def __init__(self, key):
        self._key = key

    @abc.abstractmethod
    def change_scenario(self, scenario):
        #return {key: new_value}
        pass


class PVRandomNumber(PostVariation):

    def __init__(self, key):
        super(PVRandomNumber, self).__init__(key=key)

    def change_scenario(self, scenario):
        change_value


class PVDescription(PostVariation):
        
    def __init__(self, key):
        super(PVDescription, self).__init__(key=key)
    
    def change_scenario(self, scenario):
        pass


class PVScenarioName(PostVariation):
    
    def __init__(self, key):
        super(PVScenarioName, self).__init__(key=key)
    
    def change_scenario(self, scenario):
        pass