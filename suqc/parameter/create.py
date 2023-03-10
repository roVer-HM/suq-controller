#!/usr/bin/env python3
from __future__ import annotations
import abc
import multiprocessing
import os
from typing import Callable, Protocol, Tuple, List
import warnings
from distutils.dir_util import copy_tree

import suqc.request  # no "from suqc.request import ..." works because of circular imports
import suqc.requestitem
from suqc.environment import AbstractEnvironmentManager
from suqc.parameter.postchanges import PostScenarioChangesBase
from suqc.parameter.sampling import ParameterVariationBase
from suqc.utils.dict_utils import change_dict, deep_dict_lookup
from suqc.utils.general import create_folder, njobs_check_and_set, remove_folder
from omnetinireader.config_parser import updateConfigFile

    

class ScenarioCreationCopyFunction(Protocol):
    """Copy files to a specific  simulation (aka RequestItem). These functions are called after 
    all runs are generated. Thus the scenario and or ini file already exist in the RequestItem location
    and can be used in any way. 
    """

    def copy_files(self, env_man: AbstractEnvironmentManager, item:suqc.requestitem.RequestItem):
        pass

def opp_creator(env_man, parameter_variation, njobs, copy_f:List[ScenarioCreationCopyFunction]|None = None):
        scenario_creation = CrownetCreation(env_man, parameter_variation)
        if copy_f is not None:
            scenario_creation.file_copy_functions = copy_f
        return  scenario_creation.generate_scenarios(njobs)

def coupled_creator(env_man, parameter_variation, njobs, copy_f:List[ScenarioCreationCopyFunction]|None = None):
        scenario_creation = CoupledScenarioCreation(env_man, parameter_variation)
        if copy_f is not None:
            scenario_creation.file_copy_functions = copy_f
        return  scenario_creation.generate_scenarios(njobs)

class AbstractScenarioCreation(object):
    def __init__(
            self,
            env_man: AbstractEnvironmentManager,
            parameter_variation: ParameterVariationBase,
            post_change: PostScenarioChangesBase = None,
    ):
        self._env_man = env_man
        self._parameter_variation = parameter_variation
        self._post_changes = post_change
        self._sampling_check_selected_keys()
        self.file_copy_functions: List[ScenarioCreationCopyFunction] = []

    @abc.abstractmethod
    def _sampling_check_selected_keys(self):
        raise NotImplemented

    @abc.abstractmethod
    def _sp_creation(self) -> List[suqc.requestitem.RequestItem]:
        raise NotImplemented

    @abc.abstractmethod
    def _mp_creation(self, njobs) -> List[suqc.requestitem.RequestItem]:
        raise NotImplemented

    # public methods
    def generate_scenarios(self, njobs):

        ntasks = self._parameter_variation.points.shape[0]
        njobs = njobs_check_and_set(njobs=njobs, ntasks=ntasks)

        # increases readability and promotes shorter paths (apparently lengthy paths can cause problems on Windows)
        # see issue #76
        self._adapt_nr_digits_env_man(
            nr_variations=self._parameter_variation.nr_parameter_variations(),
            nr_runs=self._parameter_variation.nr_scenario_runs(),
        )

        target_path = self._env_man.get_env_outputfolder_path()

        # For security:
        remove_folder(target_path)
        create_folder(target_path)

        if njobs == 1:
            request_item_list = self._sp_creation()
        else:
            request_item_list = self._mp_creation(njobs)
        
        for item in request_item_list:
            # copy additional files specific for each request item.
            for copy_f in self.file_copy_functions:
                copy_f.copy_files(self._env_man, item)

        return request_item_list

    # private methods
    def _adapt_nr_digits_env_man(self, nr_variations, nr_runs):
        self._env_man.nr_digits_variation = len(str(nr_variations))
        self._env_man.nr_digits_runs = len(str(nr_runs))

    ## vadere specific

    def _create_vadere_scenario(
            self, args
    ):  
        # TODO: how do multiple arguments work for pool.map functions? (see below)
        """Set up a new scenario and return info of parameter id and location."""
        parameter_id = args[0]  # TODO: this would kind of reduce this ugly code
        run_id = args[1]
        parameter_variation = args[2]

        base_scenario_file = self._env_man.scenario_provider.get_base_scenario(
            parameter_id, run_id
        )
        par_var_scenario = change_dict(
            base_scenario_file, changes=parameter_variation
        )

        if self._post_changes is not None:
            # Apply pre-defined changes to each scenario file
            new_scenario = self._post_changes.change_scenario(
                scenario=par_var_scenario,
                parameter_id=parameter_id,
                run_id=run_id,
                parameter_variation=parameter_variation,
            )
        else:
            new_scenario = par_var_scenario

        output_folder = self._env_man.get_variation_output_folder(parameter_id, run_id)
        self._print_scenario_warnings(new_scenario)
        scenario_path = self._env_man.save_scenario_variation(
            parameter_id, run_id, new_scenario
        )

        result_item = suqc.requestitem.RequestItem(
            parameter_id=parameter_id,
            run_id=run_id,
            scenario_path=scenario_path,
            base_path=self._env_man.base_path,
            output_folder=output_folder,
        )
        return result_item

    def _print_scenario_warnings(self, scenario):
        try:
            real_time_sim_time_ratio, _ = deep_dict_lookup(
                scenario, "realTimeSimTimeRatio"
            )
        except Exception:
            real_time_sim_time_ratio = (
                0  # ignore this warning if the lookup failed for whatever reason.
            )

        if real_time_sim_time_ratio > 1e-14:
            warnings.warn(
                f"In a scenario the key 'realTimeSimTimeRatio={real_time_sim_time_ratio}'. Large values "
                f"slow down the evaluation speed."
            )

    ## omnet specific
    def _create_omnet_scenario(
            self, args
    ):  # TODO: how do multiple arguments work for pool.map functions? (see below)
        """Set up a new scenario and return info of parameter id and location."""
        parameter_id = args[0]  # TODO: this would kind of reduce this ugly code
        run_id = args[1]
        parameter_variation = args[2]

        output_path = self.write_changed_ini_file(parameter_id, parameter_variation, run_id)
        # needed output to create result item in CrownetSumo case
        return output_path

    def write_changed_ini_file(self, parameter_id, parameter_variation, run_id):
        par_var_scenario = updateConfigFile(self._env_man.omnet_basis_ini, changes=parameter_variation, deepcopy=True)
        output_path = self._env_man.scenario_variation_path(
            parameter_id, run_id, simulator="omnet"
        )
        with open(output_path, "w") as outfile:
            # only save selected config hierarchy (better readability and helps debugging)
            par_var_scenario.writer(outfile, selected_config_only=True)
        return output_path

    def copy_simulation_files(self, output_path):
        folder = os.path.dirname(output_path)
        ini_path = os.path.join(self._env_man.env_path, "additional_rover_files")
        copy_tree(ini_path, folder)


class VadereScenarioCreation(AbstractScenarioCreation):
    def __init__(
            self,
            env_man: AbstractEnvironmentManager,
            parameter_variation: ParameterVariationBase,
            post_change: PostScenarioChangesBase = None,
    ):
        super().__init__(env_man, parameter_variation, post_change)

    def _sp_creation(self) -> List[suqc.requestitem.RequestItem]:
        """Single process loop to create all requested scenarios."""
        request_item_list = []
        for par_id, run_id, par_change in self._parameter_variation.par_iter():
            request_item_list.append(
                self._create_vadere_scenario([par_id, run_id, par_change])
            )
        return request_item_list

    def _mp_creation(self, njobs) -> List[suqc.requestitem.RequestItem]:
        """Multi process function to create all requested scenarios."""
        pool = multiprocessing.Pool(processes=njobs)
        request_item_list = pool.map(
            self._create_vadere_scenario, self._parameter_variation.par_iter()
        )
        return request_item_list

    def _sampling_check_selected_keys(self):
        self._parameter_variation.check_vadere_keys(self._env_man.scenario_provider)


class CoupledScenarioCreation(AbstractScenarioCreation):
    def __init__(
            self,
            env_man: AbstractEnvironmentManager,
            parameter_variation: ParameterVariationBase,
            post_change: PostScenarioChangesBase = None,
    ):
        super().__init__(env_man, parameter_variation, post_change)

    def is_omnet_in_parameter_variation(self) -> bool:
        return False

    def _sp_creation(self):
        """Single process loop to create all requested scenarios."""

        # copy all content from simulations to new folder --->  copy_folder_to_new(from, to)
        # if omnet
        #  - configure ini file (par_iter) configure_ini_file(path_to_ini) ->
        #  - copy configured_ini file (self_create_omnet_scenario) ->
        # copy simulation files

        # omnet specific
        variations_omnet = self._parameter_variation.par_iter(simulator="omnet")
        for par_id, run_id, par_change in variations_omnet:
            output_path = self._create_omnet_scenario([par_id, run_id, par_change])
            self.copy_simulation_files(output_path)

        # vadere specific
        request_item_list = list()
        variations_vadere = self._parameter_variation.par_iter(simulator="vadere")
        for par_id, run_id, par_change in variations_vadere:
            request_item_list.append(
                self._create_vadere_scenario([par_id, run_id, par_change])
            )

        return request_item_list

    def _mp_creation(self, njobs):
        """Multi process function to create all requested scenarios."""
        pool = multiprocessing.Pool(processes=njobs)

        variations_omnet = self._parameter_variation.par_iter(simulator="omnet")
        pool.map(self._create_omnet_scenario, variations_omnet)

        variations_vadere = self._parameter_variation.par_iter(simulator="vadere")
        request_item_list = pool.map(self._create_vadere_scenario, variations_vadere)
        return request_item_list

    def _sampling_check_selected_keys(self):

        #self._env_man.scenario_provider.vadere_path_basis_scenario = self._env_man.vadere_path_basis_scenario

        self._parameter_variation.check_vadere_keys(self._env_man.scenario_provider)
        self._parameter_variation.check_omnet_keys(self._env_man.omnet_basis_ini)


class CrownetCreation(AbstractScenarioCreation):

    def __init__(self,
                 env_man: AbstractEnvironmentManager,
                 parameter_variation: ParameterVariationBase):
        super().__init__(env_man, parameter_variation)

    def _sampling_check_selected_keys(self):
        # do not check keys here. CrownetCreation supports vadere, sumo and omnet(inet) mobility settings
        pass

    def _create_omnet_scenario(self, args) -> suqc.requestitem.RequestItem:
        ini_path = super()._create_omnet_scenario(args)
        return suqc.requestitem.RequestItem(
            parameter_id=args[0],
            run_id=args[1],
            scenario_path=ini_path,
            base_path=self._env_man.base_path,
            output_folder=self._env_man.get_variation_output_folder(args[0], args[1]))

    def _sp_creation(self):
        # omnet specific
        request_item_list = []
        variations_omnet = self._parameter_variation.par_iter(simulator="omnet")
        for par_id, run_id, par_change in variations_omnet:
            item = self._create_omnet_scenario([par_id, run_id, par_change])
            request_item_list.append(item)
            self.copy_simulation_files(item.scenario_path) # todo....

        return request_item_list

    def _mp_creation(self, njobs):
        """Multi process function to create all requested scenarios."""
        pool = multiprocessing.Pool(processes=njobs)

        variations_omnet = self._parameter_variation.par_iter(simulator="omnet")
        request_item_list = pool.map(self._create_omnet_scenario, variations_omnet)

        return request_item_list
