#!/usr/bin/env python3

import multiprocessing

from suqc.environment import EnvironmentManager
from suqc.parameter.sampling import ParameterVariationBase
from suqc.parameter.postchanges import PostScenarioChangesBase

from suqc.utils.general import create_folder, remove_folder, njobs_check_and_set
from suqc.utils.dict_utils import change_dict

import suqc.request  # no "from suqc.request import ..." works because of circular imports


class VadereScenarioCreation(object):

    def __init__(self, env_man: EnvironmentManager, parameter_variation: ParameterVariationBase,
                 post_change: PostScenarioChangesBase = None):

        self._env_man = env_man
        self._par_var = parameter_variation
        self._sc_change = post_change

        self._basis_scenario = self._env_man.basis_scenario
        self._par_var.check_selected_keys(self._basis_scenario)

    def _create_new_vadere_scenario(self, scenario: dict, parameter_id: int, run_id: int, parameter_variation: dict):

        par_var_scenario = change_dict(scenario, changes=parameter_variation)

        if self._sc_change is not None:
            # Apply pre-defined changes to each scenario file
            final_scenario = self._sc_change.change_scenario(scenario=par_var_scenario,
                                                             parameter_id=parameter_id,
                                                             run_id=run_id,
                                                             parameter_variation=parameter_variation)
        else:
            final_scenario = par_var_scenario

        return final_scenario

    def _save_vadere_scenario(self, par_id, run_id, scenario):
        fp = self._env_man.save_scenario_variation(par_id, run_id, scenario)
        return fp

    def _create_scenario(self, args):  # TODO: how do multiple arguments work for pool.map functions? (see below)
        """Set up a new scenario and return info of parameter id and location."""
        parameter_id = args[0]  # TODO: this would kind of reduce this ugly code
        run_id = args[1]
        parameter_variation = args[2]

        new_scenario = self._create_new_vadere_scenario(self._basis_scenario, parameter_id, run_id, parameter_variation)

        output_folder = self._env_man.get_variation_output_folder(parameter_id, run_id)
        scenario_path = self._save_vadere_scenario(parameter_id, run_id, new_scenario)

        result_item = suqc.request.RequestItem(parameter_id=parameter_id,
                                               run_id=run_id,
                                               scenario_path=scenario_path,
                                               base_path=self._env_man.base_path,
                                               output_folder=output_folder)
        return result_item

    def _sp_creation(self):
        """Single process loop to create all requested scenarios."""

        request_item_list = list()
        for par_id, run_id, par_change in self._par_var.par_iter():
            request_item_list.append(self._create_scenario([par_id, run_id, par_change]))
        return request_item_list

    def _mp_creation(self, njobs):
        """Multi process function to create all requested scenarios."""
        pool = multiprocessing.Pool(processes=njobs)
        request_item_list = pool.map(self._create_scenario, self._par_var.par_iter())
        return request_item_list

    def _adapt_nr_digits_env_man(self, nr_variations, nr_runs):
        self._env_man.nr_digits_variation = len(str(nr_variations))
        self._env_man.nr_digits_runs = len(str(nr_runs))

    def generate_vadere_scenarios(self, njobs):

        ntasks = self._par_var.points.shape[0]
        njobs = njobs_check_and_set(njobs=njobs, ntasks=ntasks)

        # increases readability and promotes shorter paths (apparently lengthy paths can cause problems on Windows)
        # see issue #76
        self._adapt_nr_digits_env_man(nr_variations=self._par_var.nr_parameter_variations(),
                                      nr_runs=self._par_var.nr_scenario_runs())

        target_path = self._env_man.get_env_outputfolder_path()

        # For security:
        remove_folder(target_path)
        create_folder(target_path)

        basis_scenario = self._env_man.basis_scenario
        self._par_var.check_selected_keys(basis_scenario)

        if njobs == 1:
            request_item_list = self._sp_creation()
        else:
            request_item_list = self._mp_creation(njobs)

        return request_item_list
