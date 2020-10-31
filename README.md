# What is the suq-controller?

The suq-controller is a Python package for the open source microscopic pedestrian simulator Vadere. The sampling is automated and can be parallelized. All results are returned in a convenient format ([pandas DataFrame](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html)). 

The main motivation is to provide a tool to build Surrogate (S) or Uncertainty Quantification (UQ) models. 


### Work in progress
Note, that the project is a work in progress. Features are only implemented when required and we welcome contributions (feedback, code, documentation, tests, ...). Please interact through issues.  

# Install

Use Python's package mangement tool and install with

```
python3 -m pip install git+https://gitlab.lrz.de/vadere/suq-controller.git@master
```

Test if the installed package was installed successfully by running:

```
python3 -c "import suqc; print(suqc.__version__)"
```

This command should print the installed version number (and potentially infos to set up required folder) in the terminal. 

**Requirements:**

- Python>=3.6
- Other packages listed in `requirements.txt `.

#### Use source directly:

Run the code from the source directly (without install), please check if you meet the requirements (see `requirements.txt` file). You can also run `pip3 install -r /path/to/requirements.txt`. Make also sure that the Python paths are set correctly (possibly add with `sys`). 


### Tutorials

See [SRC_PATH]/tutorial


### Contributing and mirror SUQC into Vadere/Tools

Please only contribute (report bugs, code, ideas, etc.) in the original repository. 

https://gitlab.lrz.de/vadere/suq-controller/

To update the suq-controller with the current master run the following git command from Vadere's root source code path:

```
git subtree pull --prefix Tools/SUQController git@gitlab.lrz.de:vadere/suq-controller.git master --squash
```

#### Using SUQC and Vadere 
A few hints for your Vadere `.scenario` files:

1.  ScenarioChecker  
    Before running your scenario automatically on suqc, activate the ``ScenarioChecker`` (Project > Activate ScenarioChecker) and run it in the ``VadereGui``.
   The ScenarioChecker will point out potential problems with your scenario file. 
2.  Default parameters  
    Make sure to set ``realTimeSimTimeRatio`` to 0.0. (Values > 0.0 slow down the simulation for the visualisation)  
    Another point that may cost a lot of computation time is the ``optimizationType``, consider using ``DISCRETE`` (discrete optimization) instead of ``NELDER_MEAD``. Please note, that ``varyStepDirection`` should always be activated with discrete optimization.  
    Remove ``attributesCar`` from the .scenario file if you are not using any vehicles to avoid confusion of attributes. 
3.  Visual check   
    Visually check the results of your simulation, maybe check upper and lower parameter bounds. 
4.  Clean topography  
    Remove elements in your topography that are not used. Sometimes through the interaction with the mouse, tiny obstacles or targets are created unintentionally. 
    Check the elements in your topography, you can take a look at the ``ElementTree`` in the Topography creator tab. Remove all elements that are unused, especially focusing on targets. 
5.  Data processors  
    Remove all data processors and output files that you don't use. In particular, remove the overlap processors, they are intended for testing purposes. 
6.  Reproducibility  
    Make sure that your runs are reproducible - work with a ``fixedSeed`` by activating ``useFixedSeed`` or save all the ``simulationSeed``s that have been used. 
   (Another way is to provide a ``fixedSeed`` for each runs with suqc, in this case make sure that ``useFixedSeed`` is true.)


