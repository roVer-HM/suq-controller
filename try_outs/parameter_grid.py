#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

from typing import Union

# http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.ParameterSampler.html
from sklearn.model_selection import ParameterGrid, ParameterSampler

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


# suggestion to split this module in 2 parts:

# 1) is a class that can be used from user side (in UQ/SM) to define a parameter grid (carry out many checks to prevent
#   -- consists from a parameter and time sampling
#   -- carrys out many checks top prevent malformed/unexpected/"random" .scenario files
#   -- provides an iterator to iterate easily through the points set
#
# 2) a method (or if necessary class) that generates all the different scenario files according to the parameter
# class 1) defined


class ParameterVariation(object):

    def __init__(self):
        self._points = []

    def add_single_point(self):
        pass

    def add_multiple_points(self):
        pass

    def add_sklearn_grid(self, grid: Union[ParameterGrid, ParameterSampler]):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        pass


def _generate_scenarios(var: ParameterVariation):
    pass
