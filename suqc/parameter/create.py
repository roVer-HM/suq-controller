#!/usr/bin/env python3

import multiprocessing
import os
import warnings
from distutils.dir_util import copy_tree

import suqc.request  # no "from suqc.request import ..." works because of circular imports
from suqc.environment import AbstractEnvironmentManager, EnvironmentManager
from suqc.parameter.postchanges import PostScenarioChangesBase
from suqc.parameter.sampling import ParameterVariationBase
from suqc.utils.dict_utils import change_dict, change_dict_ini, deep_dict_lookup
from suqc.utils.general import create_folder, njobs_check_and_set, remove_folder


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

        self._basis_scenario = self._env_man.basis_scenario
        self._basis_ini = env_man.basis_ini
        self._sampling_check_selected_keys()

    def _create_new_vadere_scenario(
        self, scenario: dict, parameter_id: int, run_id: int, parameter_variation: dict
    ):

        par_var_scenario = change_dict(scenario, changes=parameter_variation)

        if self._post_changes is not None:
            # Apply pre-defined changes to each scenario file
            final_scenario = self._post_changes.change_scenario(
                scenario=par_var_scenario,
                parameter_id=parameter_id,
                run_id=run_id,
                parameter_variation=parameter_variation,
            )
        else:
            final_scenario = par_var_scenario

        return final_scenario

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

    def _save_vadere_scenario(self, parameter_id, run_id, scenario):

        self._print_scenario_warnings(scenario)

        fp = self._env_man.save_scenario_variation(parameter_id, run_id, scenario)
        return fp

    def _create_scenario(
        self, args
    ):  # TODO: how do multiple arguments work for pool.map functions? (see below)
        """Set up a new scenario and return info of parameter id and location."""
        parameter_id = args[0]  # TODO: this would kind of reduce this ugly code
        run_id = args[1]
        parameter_variation = args[2]

        new_scenario = self._create_new_vadere_scenario(
            self._basis_scenario, parameter_id, run_id, parameter_variation
        )

        output_folder = self._env_man.get_variation_output_folder(parameter_id, run_id)
        scenario_path = self._save_vadere_scenario(parameter_id, run_id, new_scenario)

        result_item = suqc.request.RequestItem(
            parameter_id=parameter_id,
            run_id=run_id,
            scenario_path=scenario_path,
            base_path=self._env_man.base_path,
            output_folder=output_folder,
        )
        return result_item

    def _sp_creation(self):
        """Single process loop to create all requested scenarios."""

        request_item_list = list()
        for par_id, run_id, par_change in self._parameter_variation.par_iter():
            request_item_list.append(
                self._create_scenario([par_id, run_id, par_change])
            )
        return request_item_list

    def _mp_creation(self, njobs):
        """Multi process function to create all requested scenarios."""
        pool = multiprocessing.Pool(processes=njobs)
        request_item_list = pool.map(
            self._create_scenario, self._parameter_variation.par_iter()
        )
        return request_item_list

    def _adapt_nr_digits_env_man(self, nr_variations, nr_runs):
        self._env_man.nr_digits_variation = len(str(nr_variations))
        self._env_man.nr_digits_runs = len(str(nr_runs))

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

        return request_item_list


class VadereScenarioCreation(AbstractScenarioCreation):
    def __init__(
        self,
        env_man: AbstractEnvironmentManager,
        parameter_variation: ParameterVariationBase,
        post_change: PostScenarioChangesBase = None,
    ):

        super().__init__(env_man, parameter_variation, post_change)

    def _sampling_check_selected_keys(self):
        self._parameter_variation.check_selected_keys(self._basis_scenario)


class CoupledScenarioCreation(AbstractScenarioCreation):
    def __init__(
        self,
        env_man: AbstractEnvironmentManager,
        parameter_variation: ParameterVariationBase,
        post_change: PostScenarioChangesBase = None,
    ):

        super().__init__(env_man, parameter_variation, post_change)

    def _create_scenario(
        self, args
    ):  # TODO: how do multiple arguments work for pool.map functions? (see below)
        """Set up a new scenario and return info of parameter id and location."""
        parameter_id = args[0]  # TODO: this would kind of reduce this ugly code
        run_id = args[1]
        parameter_variation = args[2]

        new_scenario = self._create_new_vadere_scenario(
            self._basis_scenario, parameter_id, run_id, parameter_variation
        )

        output_folder = self._env_man.get_variation_output_folder(parameter_id, run_id)
        scenario_path = self._save_vadere_scenario(parameter_id, run_id, new_scenario)

        result_item = suqc.request.RequestItem(
            parameter_id=parameter_id,
            run_id=run_id,
            scenario_path=scenario_path,
            base_path=self._env_man.base_path,
            output_folder=output_folder,
        )
        return result_item

    def _sp_creation(self):
        """Single process loop to create all requested scenarios."""

        variations_omnet = self._parameter_variation.par_iter(simulator="omnet")
        for par_id, run_id, par_change in variations_omnet:
            par_var_scenario = change_dict_ini(self._basis_ini, changes=par_change)
            output_path = self._env_man.scenario_variation_path(
                par_id, run_id, simulator="omnet"
            )

            with open(output_path, "w") as outfile:
                par_var_scenario.writer(outfile)

            folder = os.path.dirname(output_path)
            ini_path = os.path.join(self._env_man.env_path, "additional_rover_files")

            copy_tree(ini_path, folder)

        request_item_list = list()
        variations_vadere = self._parameter_variation.par_iter(simulator="vadere")
        for par_id, run_id, par_change in variations_vadere:
            request_item_list.append(
                self._create_scenario([par_id, run_id, par_change])
            )

        return request_item_list

    def _sampling_check_selected_keys(self):

        # vadere
        self._parameter_variation.check_selected_keys(
            self._basis_scenario, simulator="vadere"
        )

        # omnet
        # self._parameter_variation.check_selected_keys(self._basis_scenario, simulator="omnet")

    def _create_new_omnet_scenario(self):

        simulator_check = (
            self._parameter_variation.points.Parameter.keys()
            .get_level_values(0)
            .to_list()
        )

        if "omnet" in simulator_check:
            variations = self._parameter_variation.par_iter(simulator="omnet")
        else:
            variations = self._parameter_variation.par_iter()

        for par_id, run_id, par_change in variations:

            if "omnet" in simulator_check:
                par_var_scenario = change_dict_ini(self._basis_ini, changes=par_change)
            else:
                par_var_scenario = self._basis_ini

            output_path = self._env_man.scenario_variation_path(
                par_id, run_id, simulator="omnet"
            )

            with open(output_path, "w") as outfile:
                par_var_scenario.writer(outfile)

            folder = os.path.dirname(output_path)
            ini_path = os.path.join(self._env_man.env_path, "additional_rover_files")

            copy_tree(ini_path, folder)
