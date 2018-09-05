### WORK IN PROGRESS

The suq-controller connects the modules "Uncertainty Quantification" and "Surrogate Model" (see other vadere/ Repos). 
The main functionality of the suq-controller is to query multiple (differently parametrized) VADERE scenarios and return the results of a quantity of interest (QoI) in a convenient format. 


This git repository uses git large file storage (git-lfs). Primarily this is to track the VADERE .jar files without storing them directly in the history. 

To install git-lfs follow the instructions here: https://github.com/git-lfs/git-lfs/wiki/Installation

In the repo the file `.gitattributes` shows the settings for git-lfs. 




#### Getting started


1. Download and install:


Download source code with git:
```
git@gitlab.lrz.de:vadere/suq-controller.git
```

Install package `suqc` by running the following command inside the downloaded folder `suq-contoller`. It is recommended 
to use `python>=3.6`.

```
python3 setup.py install
``` 

This installs the essential package, but does not copy the the models or example container consisting of one environment. These will be set as an example in the following points. 
Note: This may have to be executed with `sudo` in Linux. 

Test if the installed package was installed successfully by running (TODO: do with printing the version of suqc):

```
python3 -c "import suqc"
```

This command should silently exectue and not throw an error. 


2. Configuration of suqc

During the installation process two folders are created at the user's home path. 

   1. `.suqc` consists of the meta configuration of the suq-controller. This includes the path to the 
   environment-container folder and the path where the models are located. 
   2. `suqc_envs` this is where the scenario environments are


##### Set a "link" to a new VADERE model

```
import suqc 
suqc.configuration.set_new_model(name="vadere_v0.1", path="PATH_TO_JAR_FILE")
```

The name is the identifier of which model should be used when issuing a query (see below). 



#### Set a new environment container

To link to a new environment container the path can be set with the command:

```
import suqc 
suqc.configuration.set_con_path(path="PATH_FOLDER")
```
Initially, the new folder should either an empty or already consist of suq-environments. 

#### Set link to a new VADERE model 

It is possible to set multiple models and container paths in the suq-controller. All available models and container paths can be displayed:

```
import suqc
suqc.configuration.set_new_model(name="vadere_v0.1", path="PATH_TO_JAR_FILE")
```


