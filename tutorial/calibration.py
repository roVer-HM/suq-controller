import numpy as np
from scipy.optimize import minimize

from sklearn.preprocessing import minmax_scale

import sys
import time

from tutorial.imports import *

# This is just to make sure that the systems path is set up correctly, to have correct imports, it can be ignored:
sys.path.append(os.path.abspath("."))
sys.path.append(os.path.abspath(".."))

default_f1 = None
default_f2 = None


def vadere_simulator(x,f10,f20, bounds):

    reps = 1
    x = np.array( [ denormalize(x,b[0],b[1])  for (x,b)  in zip(x,bounds) ] )

    
    sys.stdout = open(os.devnull, 'w')

    vadere = os.environ["VADERE"]  # system variable to vadere repo

    outputfolder = os.path.join(os.getcwd(), "calibration")

    if os.path.exists(outputfolder):
        shutil.rmtree(outputfolder)

    os.makedirs(outputfolder)
    out_dir = f"run__{time.time()}"

    par_var = [
        {
            "pedPotentialIntimateSpaceWidth": x[0], # 0.45
            "pedPotentialPersonalSpaceWidth": x[1], # 1.2
            "pedPotentialHeight": x[2], # 50.0
            "intimateSpaceFactor": 1.2, # 1.2
            "personalSpacePower": 1.0, # 1.0
            "intimateSpacePower": 1.0, # 1.0
        },
    ]

    setup = DictVariation(  # path to a Vadere .scenario file (the one to sample)
        scenario_path=os.path.join(
            vadere, "Scenarios/Demos/supermarket/scenarios/Liddle_osm_v4.scenario"
        ),
        # parameter key to change
        parameter_dict_list=par_var,
        # output file name to collect
        qoi=["contacts.txt", "conts.txt", "endtime.txt"],
        # path to Vadere console jar file or use
        # VadereConsoleWrapper for more options
        model=VadereConsoleWrapper(
            model_path=os.path.join(
                vadere, "VadereSimulator/target/vadere-console.jar"
            ),
            jvm_flags=["-enableassertions"],
        ),
        # specify how often each scenario should run
        scenario_runs=reps,
        # post changes can be used to apply changes to the scenario that are not part of the
        # sampling -- especially random seed setting. It is easy to define user based changes.
        post_changes=PostScenarioChangesBase(apply_default=True),
        # specify the path, where the results are written
        output_path=outputfolder,
        # specify the folder to write vadere output files to
        output_folder=out_dir,
        # flag whether to remove the output_folder after the run
        remove_output=False,
    )

    par_var, data = setup.run(njobs=-1)

    print("---------------------------------------\n \n")
    print("ALL USED PARAMETER:")
    print(par_var)

    print("COLLECTED DATA:")
    print(data)



    endtimes = np.array(data["endtime.txt"].values).ravel()
    endtimes = endtimes[endtimes <= 79.9] # 80 endtime

    f1 = len(endtimes)  # make sure that pedestrians reach other side 0 ... 50

    conts_15 = data["contacts.txt"]
    conts_15 = conts_15['durationTimesteps-PID5'].values.tolist()
    if len(conts_15) == 0:
        f2 = 0
    else:
        f2 = np.sum( np.array([int(a)*0.1 for a in conts_15 if a.isnumeric()]))  # 0.1 bug! should be 1



    sys.stdout = sys.__stdout__

    if f10 is None:
        f10 = f1

    if f20 is None:
        f20 = f2


    f = -0.1* f1 / f10 + 0.9* f2 / f20

    x_str = ' '.join([f"{xi:.4f}" for xi in x])

    print(f"Parameter values x = {x_str}. Objective function vals f1 = {f1}, f2 = {f2}, normalized: f1 = {f1/f10}, f2 = {f2/f20}, f = {f}")

    return f, f1, f2

def vadere_simulator_nm(x, f1, f2, bounds):
    f,__,__ = vadere_simulator(x, f1, f2, bounds)
    return f


def normalize(value, min, max):
    normalized = (value - min) / (max - min)
    return normalized

def denormalize(value, min, max):
    denormalized = min + value*(max - min)
    return denormalized


# NOTE: If running this script twice, there is an user input required. Because an "output folder" already exists from
# the first run, this output folder gets replaced with the next run. Therefore, the old output is removed.

if __name__ == "__main__":  # main required by Windows to run in parallel
    ###############################################################################################################

    x0 = np.array([1.0,2.0,150.0])
    bounds = ((0.45,1.5),(1.2, 5.0),(50.0, 500.0))
    x0_normalized = np.array( [ normalize(x0i,b[0],b[1])  for (x0i,b)  in zip(x0,bounds) ] )
    bounds_normalized = [(0,1) for __ in range(len(bounds))]

    f,f1,f2 = vadere_simulator(x0_normalized,None,None,bounds)


    res = minimize(
        vadere_simulator_nm,
        x0_normalized,
        args=(f1,f2, bounds),
        method="SLSQP",
        options={"disp": True, "maxiter": 2, 'eps': 0.001}, #
        bounds=bounds_normalized
    )

