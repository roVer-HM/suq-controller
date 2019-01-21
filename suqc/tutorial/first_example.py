#!/usr/bin/env python3 

import numpy as np
import os
import urllib

from suqc import single_key_request, quick_request

# Downloads a Vadere model used in this example, if not already here -- can be ignored.
if not os.path.exists("vadere0_7rc.jar"):
    # downloads file if it does not exist in this folder
    urllib.request.urlretrieve("https://syncandshare.lrz.de/dl/fi6svHdgohH5np2ErsjYGMoy",
                               "vadere0_7rc.jar")

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------

# Set important paths:
path2folder = os.path.dirname(os.path.realpath(__file__))
path2model = os.path.join(path2folder, "vadere0_7rc.jar")
path2scenario = os.path.join(path2folder, "example.scenario")

###############################################################################################################
# First example
# Usecase: One parameter in the scenario is changed, for every independent the data is collected and returned.
# The Vadere output is deleted after all scenarios run.

# Example where the values of 'speedDistributionMean' are set between 0.1 and 1.5 in 5 equidistant points

par_var, data = single_key_request(scenario_path=path2scenario,  # -> path to the Vadere .scenario file to vary
                                   key="speedDistributionMean",  # -> parameter key to change
                                   values=np.linspace(0.7, 1.5, 3),  # -> values to set for the parameter
                                   qoi="density.txt",  # -> output file name to collect
                                   model=path2model)  # -> path to Vadere console jar file to use for simulation

print("---------------------------------------\n \n")
print(" C A S E    1")
print("ALL USED PARAMETER:")
print(par_var)

print("COLLECTED DATA:")
print(data)

###############################################################################################################
# Second example:
# Usecase: Set yourself the parameters you want to change. Do this by defining a list of dictionaries with the
# corresponding parameter. Again, the Vadere output is deleted after all scenarios run.

# Set own values to vary, they don't have to be the same - in the first run acceleration is left to default.
par_var = [{"speedDistributionMean": 1.0, "maximumSpeed": 3.0},
           {"speedDistributionMean": 1.3, "maximumSpeed": 4.0, "acceleration": 3.0}]


par_var, data = quick_request(scenario_path=path2scenario,
                              parameter_var=par_var,
                              qoi="density.txt",
                              model=path2model,
                              njobs=-1)  # -1 indicates to use all cores available to parallelize the scenarios

print("\n \n ---------------------------------------\n \n")
print(" C A S E    2")
print("ALL USED PARAMETER:")
print(par_var)

print("COLLECTED DATA:")
print(data)