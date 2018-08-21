WORK IN PROGRESS

The suq-controller connects the modules "Uncertainty Quantification" and "Surrogate Model" (see other vadere/ Repos). 
The main functionality of the suq-controller is to query multiple (differently parametrized) Vadere scenarios and return the results of a quantity of interest (QoI) in a convenient format. 


This git repository uses git large file storage (git-lfs). Primarily this is to track the VADERE .jar files without storing them directly in the history. 

To install git-lfs follow the instructions here: https://github.com/git-lfs/git-lfs/wiki/Installation

After running `git lfs install` make sure to track the `jar` files by running the command:

```
git lfs track ".*jar"
```
