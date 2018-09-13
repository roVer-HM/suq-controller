### WORK IN PROGRESS

The suq-controller connects the modules "Surrogate Model" (S) and "Uncertainty Quantification" (UQ) (see other vadere Repos). 
The main functionality of the `suq-controller` is to query many differently parametrized VADERE scenarios and 
return the result of specified quantity of interests (QoI) in a convenient format ([pandas DataFrame](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html)). 


This git repository uses git large file storage (git-lfs). This allows to ship default VADERE models (larger .jar files.)
with the git repository. 

For developers: To install git-lfs follow the instructions [here](https://github.com/git-lfs/git-lfs/wiki/Installation)
In file `.gitattributes` in the repo shows the settings for git-lfs. 


### Glossary

Other words were used in this project to not confuse terminology with VADERE (such as `scenario` and `project`). 

* **container** is the parent folder of (multiple) environments
* **environment** is folder consisting of a specifed VADERE scenario that is intended to query
* **query** is to a user request for a specific VADERE setting, given the scenario set in the environment. A query can
also be multiple scenario settings (such as a full grid sampling)

#### Getting started


1. Download and install:

Download source code, pre-set VADERE models and example environments with git:
```
git@gitlab.lrz.de:vadere/suq-controller.git
```

Install package `suqc` by running the following command inside the downloaded folder `suq-contoller`. It is recommended 
to use `python>=3.6`.

```
python3 setup.py install
``` 

Note: In Linux this may have to be executed with `sudo`.

This installs the essential package, but does **not** copy the models or example environments. To set up the 
corresponding folders and copy the models to the appropriate position run

```
python3 setup_folders.py TODO
```
##### TODO: Make setup_folders configurable, i.e. allow to only setup folders without copying examples


Test if the installed package was installed successfully by running (TODO: do with printing the version of suqc):

```
python3 -c "import suqc; print(suqc.__version__)"
```

This command should print the installed version number in the terminal. In case an error was thrown the package is 
not installed successfully. 


2. Configuration of `suqc`

During the run of `setup_folders.py` two folders are created at the user's home path. 

   1. `.suqc` consists of the meta configuration of the suq-controller. This includes the path to the 
   environment-container folder and information about the available models. 
   2. `suqc_envs` is a container and consists of environments that are set up. 


##### Set a new VADERE model

It is possible to set multiple models and container paths in the suq-controller. 

```
import suqc.configuration as cfg
cfg.add_new_model(name="vadere_v0.1", path="PATH_TO_JAR_FILE")
```
The argument `name` is the identifier of which model should be used to simulate when a query is issued (see below). 
To set a new VADERE model a path to a .jar file has to be given. The file is copied into `$HOME/.suqc/models". 

##### Example

In the setup file `setup_folders.py` an example environment is copyied in `$HOME/suqc_envs/corner". This environment
consists of a VADERE basis file. Script to run:

```python
# TODO: simplify the importing stuff...
import suqc.configuration as scfg
import suqc.query as query
import suqc.parameter as par
import suqc.qoi as qoi

# Set up the environment to make queries
em = scfg.EnvironmentManager("corner")

# Initiate an object to define the parameters to query
pv = par.ParameterVariation(em)

# Define a grid to run the simulation, here: vary the standard distribution from 0 to 0.3 in 0.1 intervals
pv.add_dict_grid({"speedDistributionStandardDeviation": [0.0, 0.1, 0.2, 0.3]})


# Define a quantity of interest that we are interested in
q1 = qoi.PedestrianEvacuationTimeProcessor(em)

# Initiate and run (i.e. simulate) the query. Here, only a single processor is used
r = query.Query(em, qoi=q1).query_simulate_all_new(pv, njobs=1)
print(r)

# Define another, time dependent, quantity of interest 
q2 = qoi.AreaDensityVoronoiProcessor(em)

# Initiate and run (i.e. simulate) the query. Here, all available processors are used to run the simulations in parallel
r = query.Query(em, qoi=q2).query_simulate_all_new(pv, njobs=-1)
print(r)
```
