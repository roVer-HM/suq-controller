#!/usr/bin/env python3

from __future__ import annotations
import glob
import json
import multiprocessing
import os
import shutil
import subprocess

from omnetinireader.config_parser import OppConfigType

from suqc.CommandBuilder.interfaces import Command
from suqc.environment import (
    CoupledEnvironmentManager,
    AbstractEnvironmentManager,
    CrownetEnvironmentManager,
    VadereEnvironmentManager
)
from suqc.parameter.create import CoupledScenarioCreation, VadereScenarioCreation, CrownetCreation
from suqc.parameter.postchanges import PostScenarioChangesBase
from suqc.parameter.sampling import *
from suqc.qoi import VadereQuantityOfInterest, QuantityOfInterest
from suqc.remote import ServerRequest
from suqc.requestitem import RequestItem
from suqc.utils.general import (
    create_folder,
    njobs_check_and_set,
    parent_folder_clean,
    check_simulator,
)


def read_from_existing_output(
        env_path, qoi_filename, extract_ids=True, parentfolder_level=1
):
    read_data = []

    id_counter = 0

    for root, dirs, files in os.walk(env_path):
        for file in files:
            if file == qoi_filename:

                filepath = os.path.join(root, file)
                # default vals: vadere (1), rover/omnet (5)
                filepath0 = filepath
                for level_up in range(parentfolder_level):
                    filepath0 = os.path.dirname(filepath0)

                parentfolder = os.path.basename(filepath0)

                # TODO: it'd be better to use QuantityOfInterest.read_and_extract_qois
                #  here, as this is the "central unit" to read files of interest
                df_data = pd.read_csv(filepath, delimiter=" ", header=[0], comment="#")

                if extract_ids:
                    run_data = [int(i) for i in parentfolder.split("_") if i.isdigit()]

                    if (
                            all(isinstance(item, int) == True for item in run_data)
                            and len(run_data) == 2
                    ):
                        parameter_id, run_id = run_data
                    else:
                        raise ValueError("Failed to extract parameter- and run id.")

                    index = pd.MultiIndex.from_arrays(
                        [
                            np.ones(df_data.shape[0], dtype=np.int64) * parameter_id,
                            np.ones(df_data.shape[0], dtype=np.int64) * run_id,
                        ]
                    )
                else:
                    index = pd.Index(
                        np.ones(df_data.shape[0], dtype=np.int64) * id_counter
                    )
                    id_counter += 1

                df_data.index = index
                read_data.append(df_data)

    read_data = pd.concat(read_data, axis=0)

    meta_data = pd.read_csv(
        os.path.join(env_path, "metainfo.csv"), header=[0]
    ).set_index(["id", "run_id"])

    return read_data, meta_data


class Request(object):
    PARAMETER_ID = "id"
    RUN_ID = "run_id"
    REQUIRED_TIME = "required_wallclock_time"
    RETURN_CODE = "return_code"

    def __init__(
            self,
            request_item_list: List[RequestItem],
            model: Command,
            qoi: Union[VadereQuantityOfInterest, None],
            retries: int = 5
    ):
        if len(request_item_list) == 0:
            raise ValueError("request_item_list has no entries.")

        # self.model = AbstractConsoleWrapper.infer_model(model)
        self.model = model
        self.request_item_list = request_item_list
        # Can be None, if this is the case, no output data will be parsed to pd.DataFrame
        self.qoi = qoi

        # Return values as pd.DataFrame from all runs (they cannot be included directly by the runs,
        # because Python's mulitprocessing is not shared memory due to the GIL (i.e. different/independent processes
        # are created
        self.compiled_qoi_data = None
        self.compiled_run_info = None

        # Number of retries for failed simulation
        self.retries = retries

    def _interpret_return_value(self, ret_val, par_id):
        if ret_val == 0:
            return True
        else:  # ret_val != 0
            print(f"WARNING: Simulation with parameter setting {par_id} failed.")
            return False

    def _single_request(self, request_item: RequestItem) -> RequestItem:

        self._create_output_path(request_item.output_path)
        _model = deepcopy(self.model)

        _model.add_argument("-f", request_item.scenario_path)
        _model.add_argument("-o", request_item.output_path)
        return_code, required_time, output_on_error = _model.run()

        is_results = self._interpret_return_value(
            return_code, request_item.parameter_id
        )

        if is_results and self.qoi is not None:
            result = self.qoi.read_and_extract_qois(
                par_id=request_item.parameter_id,
                run_id=request_item.run_id,
                output_path=request_item.output_path,
            )
        elif not is_results and self.qoi is not None:
            # something went wrong during simulation run
            assert output_on_error is not None

            filename_stdout = "stdout_on_error.txt"
            filename_stderr = "stderr_on_error.txt"
            self._write_console_output(
                output_on_error["stdout"], request_item.output_path, filename_stdout
            )
            self._write_console_output(
                output_on_error["stderr"], request_item.output_path, filename_stderr
            )
            result = None
        else:
            result = None

        if self.qoi is not None and not is_results:
            required_time = np.nan

        request_item.add_qoi_result(result)
        request_item.add_meta_info(required_time=required_time, return_code=return_code)

        # Because of the multi-processor part, don't try to already add the results here
        # to request_item
        return request_item

    def _create_output_path(self, output_path):
        create_folder(output_path, delete_if_exists=True)
        return output_path

    def _write_console_output(self, msg, output_path, filename):
        _file = os.path.abspath(os.path.join(output_path, filename))
        os.makedirs(os.path.dirname(_file), exist_ok=True)
        if msg is not None:
            with open(_file, "wb") as out:
                out.write(msg)

    def _compile_qoi(self):

        qoi_results = [item_.qoi_result for item_ in self._successful_jobs()]

        filenames = None
        for ires in qoi_results:
            if ires is not None:
                # assumption: the keys for all elements in results are the same
                # TODO: this assumption may fail... maybe better to check for this!
                filenames = list(ires.keys())
                break

        if filenames is None:
            print(
                "WARNING: All simulations failed, only 'None' results. "
                "Look in the output folder(s) for error messages."
            )
            final_results = None
        else:
            # Successful runs are collected and are concatenated into a single
            # pd.DataFrame below
            final_results = dict()

            for filename in filenames:
                collected_df = [
                    item_[filename] for item_ in qoi_results if item_ is not None
                ]
                collected_df = pd.concat(collected_df, axis=0)

                final_results[filename] = collected_df

        if filenames is not None and len(filenames) == 1:
            # There is no need to have the key/value if only one file was requested.
            final_results = final_results[filenames[0]]

        return final_results

    def _successful_jobs(self):
        return filter(lambda item: item.return_code != -1, self.request_item_list)

    def _compile_run_info(self, data=None):

        if data is None:
            data = [
                (
                    item_.parameter_id,
                    item_.run_id,
                    item_.required_time,
                    item_.return_code,
                )
                for item_ in self._successful_jobs()
            ]
        df = pd.DataFrame(
            data,
            columns=[
                self.PARAMETER_ID,
                self.RUN_ID,
                self.REQUIRED_TIME,
                self.RETURN_CODE
            ],
        )
        df.set_index(keys=[self.PARAMETER_ID, self.RUN_ID], inplace=True)

        return df

    def _add_meta_info_multiindex(self, meta_info):
        meta_info.columns = pd.MultiIndex.from_arrays(
            [["MetaInfo"] * meta_info.shape[1], meta_info.columns]
        )
        return meta_info

    def _sp_query(self):
        # single process query

        # enumerate returns tuple(par_id, scenario filepath) see
        # ParameterVariation.generate_vadere_scenarios and
        # ParameterVariation._vars_object()
        for i, request_item in enumerate(self.request_item_list):
            if request_item.return_code != 0:
                # TODO: this causes the index error! resolve this
                self.request_item_list[i] = self._single_request(request_item)

    def _mp_query(self, njobs):
        # multi process query
        pool = multiprocessing.Pool(processes=njobs)
        self.request_item_list = pool.map(self._single_request, self.request_item_list)

    def run(self, njobs: int = 1):

        retry = 0
        while self.is_unfinished_sims_existing() and retry <= self.retries:
            if retry > 0:
                print(f"Try to re-start failed simulations (attempt {retry} out of {self.retries}).")
            try:
                self.run_simulations(njobs)
            except IndexError:
                pass
            finally:
                print(f"{self.get_nr_of_finished_sims()} simulations run successfully.")
                print(f"{self.get_nr_of_unfinished_sims()} simulations failed.")
            retry += 1

        if self.get_nr_of_finished_sims() != len(self.request_item_list):
            print(f"Results for {self.get_nr_of_unfinished_sims()} simulation are still missing."
                  f"Try to increase number_retries or start the simulations manually.")
        else:
            print(f"Required simulation runs (={self.get_nr_of_finished_sims()}) completed.")

        if self.qoi is not None:
            self.compiled_run_info = self._compile_run_info()
            self.compiled_qoi_data = self._compile_qoi()

        return self.compiled_qoi_data, self.compiled_run_info

    def is_unfinished_sims_existing(self):
        return all(self._simulations_finished()) == False

    def get_nr_of_finished_sims(self):
        is_finished = np.array(self._simulations_finished())
        count = np.count_nonzero(is_finished)
        return count

    def get_nr_of_unfinished_sims(self):
        is_finished = np.array(self._simulations_finished())
        return len(is_finished) - self.get_nr_of_finished_sims()

    def _successful_simulations(self):
        return filter(lambda item: item.return_code != -1, self.request_item_list)

    def _simulations_finished(self):
        # succesful simulations have a return_code = 0
        return [sample.return_code == 0 for sample in self.request_item_list]

    def run_simulations(self, njobs):
        # nr of rows = nr of parameter settings = #simulations
        nr_simulations = len(self.request_item_list)
        njobs = njobs_check_and_set(njobs=njobs, ntasks=nr_simulations)
        if njobs == 1:
            self._sp_query()
        else:
            self._mp_query(njobs=njobs)


class VariationBase(Request, ServerRequest):
    def __init__(
            self,
            env_man: AbstractEnvironmentManager,
            parameter_variation: ParameterVariationBase,
            # model: Union[str, AbstractConsoleWrapper],
            model: Command,
            qoi: Union[str, List[str], VadereQuantityOfInterest],
            post_changes: PostScenarioChangesBase = None,
            njobs: int = 1,
            remove_output=False,
    ):

        self.parameter_variation = parameter_variation
        self.env_man = env_man
        self.post_changes = post_changes
        self.model = model
        self.remove_output = remove_output

        if qoi is None and remove_output:
            raise ValueError(
                "Invalid parameter configuration: not collecting a qoi (qoi=None) and "
                "to not keep any output (remove_output=False)."
            )


        self.set_qoi(qoi)
        request_item_list = self.scenario_creation(njobs)

        super(VariationBase, self).__init__(request_item_list, self.model, self.qoi)
        ServerRequest.__init__(self)

    def set_qoi(self, qoi):
        if isinstance(qoi, (str, list)):
            self.qoi = VadereQuantityOfInterest(
                basis_scenario=self.env_man.vadere_basis_scenario, requested_files=qoi
            )
        elif isinstance(qoi, VadereQuantityOfInterest):
            self.qoi = qoi
        else:
            self.qoi = qoi

    def scenario_creation(self, njobs):
        scenario_creation = VadereScenarioCreation(
            self.env_man, self.parameter_variation, self.post_changes
        )
        request_item_list = scenario_creation.generate_scenarios(njobs)
        return request_item_list

    def _remove_output(self):
        if self.env_man.env_path is not None:
            shutil.rmtree(self.env_man.env_path)

    def run(self, njobs: int = 1):
        qoi_result_df, meta_info = super(VariationBase, self).run(njobs)

        # add another level to distinguish the columns with the parameter lookup
        meta_info = self._add_meta_info_multiindex(meta_info)

        lookup_df = pd.concat([self.parameter_variation.points, meta_info], axis=1)
        savepath_lookup_df = os.path.join(self.env_man.env_path, "metainfo.csv")
        lookup_df.to_csv(savepath_lookup_df)

        if self.remove_output:
            self._remove_output()

        return lookup_df, qoi_result_df

    @classmethod
    def _remote_run(cls, remote_pickle_arg_path):

        kwargs = cls.open_arg_pickle(remote_pickle_arg_path)
        env_man = VadereEnvironmentManager(
            base_path=None, env_name=kwargs["remote_env_name"]
        )

        setup = cls(
            env_man=env_man,
            parameter_variation=kwargs["parameter_variation"],
            model=kwargs["model"],
            qoi=kwargs["qoi"],
            post_changes=kwargs["post_changes"],
            njobs=kwargs["njobs"],
            remove_output=False,
        )  # the output for remote will be removed after all is transferred

        res = setup.run(kwargs["njobs"])
        cls.dump_result_pickle(res, kwargs["remote_pickle_res_path"])

    def remote(self, njobs=1):
        pickle_content = {
            "qoi": self.qoi,
            "parameter_variation": self.parameter_variation,
            "post_changes": self.post_changes,
            "njobs": njobs,
        }

        local_transfer_files = {
            "path_basis_scenario": self.env_man.vadere_path_basis_scenario
        }

        remote_result = super(VariationBase, self)._remote_ssh_logic(
            local_env_man=self.env_man,
            local_pickle_content=pickle_content,
            local_transfer_files=local_transfer_files,
            local_model_obj=self.model,
            class_name="VariationBase",
            transfer_output=not self.remove_output,
        )
        return remote_result

    def get_env_man_info(self):
        return self.env_man.get_env_info()


class CoupledDictVariation(VariationBase, ServerRequest):
    def __init__(
            self,
            ini_path: str,
            parameter_dict_list: List[dict],
            qoi: Union[str, List[str]],
            model: Command,
            post_changes=PostScenarioChangesBase(apply_default=True),
            njobs_create_scenarios=1,
            output_path=None,
            output_folder=None,
            env_remote=None,
            remove_output=False,
            config="final",
    ):

        scenario_path, simulator = self._get_scenario_path(ini_path, config=config)
        if model.is_scenario_file_set():
            raise ValueError(f"Duplicate scenario specification. \n"
                             f"Remove scenario file from model (={model}).\n"
                             f"Scenario file must be specified in .ini file only.\n"
                             f"Scenario file specified in .ini: {scenario_path}.\n"
                             f"For specification see config={config} in {ini_path}.\n")

        if simulator != "vadere":
            raise RuntimeError("expected Vadere simulator")

        self.scenario_path = scenario_path
        self.ini_path = ini_path
        self.ini_dir = os.path.dirname(ini_path)

        assert os.path.exists(ini_path) and ini_path.endswith(
            ".ini"
        ), "Filepath must exist and the file has to end with .ini"

        assert os.path.exists(scenario_path) and scenario_path.endswith(
            ".scenario"
        ), "Filepath must exist and the file has to end with .scenario"

        if env_remote is None:
            env = CoupledEnvironmentManager.create_variation_env(
                basis_scenario=self.scenario_path,
                ini_scenario=self.ini_path,
                base_path=output_path,
                env_name=output_folder,
                handle_existing="ask_user_replace",
            )
            self.env_path = env.env_path
        else:
            self.env_path = env_remote.env_path
            self.remove_output = False  # Do not remove the folder because this is done with the remote procedure
            env = env_remote

        parameter_variation = ParameterVariationBase().add_data_points(parameter_dict_list)

        super(CoupledDictVariation, self).__init__(
            env_man=env,
            parameter_variation=parameter_variation,
            model=model,
            qoi=qoi,
            post_changes=post_changes,
            njobs=njobs_create_scenarios,
            remove_output=remove_output,
        )

    def set_qoi(self, qoi):
        if isinstance(qoi, (str, list)):
            self.qoi = QuantityOfInterest(requested_files=qoi)
        elif isinstance(qoi, QuantityOfInterest):
            self.qoi = qoi
        else:
            raise ValueError(f"qoi must be of type QuantityOfInterest")

    def _get_scenario_path(self, ini_path, config="final"):

        ini_folder = os.path.dirname(ini_path)
        ini_file = OppConfigFileBase.from_path(
            ini_path=ini_path, config=config, cfg_type=OppConfigType.EDIT_GLOBAL,
        )
        scenario_name, simulator = check_simulator(ini_file)
        scenario_path = os.path.join(ini_folder, scenario_name)

        return scenario_path, simulator

    def scenario_creation(self, njobs):
        parameter_variation = self.parameter_variation

        scenario_creation = CoupledScenarioCreation(
            self.env_man, parameter_variation, self.post_changes
        )
        request_item_list = scenario_creation.generate_scenarios(njobs)

        return request_item_list

    def _single_request(self, request_item: RequestItem) -> RequestItem:
        try:
            # TODO: implement functionality in CrownetRequest._single_request
            if request_item.return_code == 0:
                return request_item
            else:
                print(
                    f"No result data found for Sample__{request_item.parameter_id}_{request_item.run_id} (return_code: {request_item.return_code}). Start simulation.")

            par_id = request_item.parameter_id
            run_id = request_item.run_id
            start_file = self.env_man.get_name_run_script_file()

            dirname = os.path.join(
                self.env_man.get_env_outputfolder_path(),
                self.env_man.get_simulation_directory(par_id, run_id),
            )

            # crate deep copy in case we run in multithreaded mode.
            _model: Command = deepcopy(self.model)
            _model.override_host_config(os.path.basename(dirname))

            _scenario = os.path.basename(self.env_man.vadere_path_basis_scenario)
            _model.scenario_file(_scenario, override=True)

            return_code, required_time = _model.run(cwd=dirname, file_name=start_file)

            print(f"Simulation {par_id} {run_id}: set return_code to {return_code} ")
            request_item.add_meta_info(required_time=required_time, return_code=return_code)
            # Because of the multi-processor part, don't try to already add the results here to _results_df
            if return_code != 0:
                return request_item

            is_results = self._interpret_return_value(
                return_code, request_item.parameter_id
            )

            if is_results and self.qoi is not None:
                result = self.qoi.read_and_extract_qois(
                    par_id=request_item.parameter_id,
                    run_id=request_item.run_id,
                    output_path=os.path.join(dirname, "results"),
                )
            else:
                result = None

            request_item.add_qoi_result(result)

            if self.remove_output is True:
                shutil.rmtree(dirname)

        except Exception as e:
            print(f"Failed. Error {e}")
            request_item.add_meta_info(required_time=-1, return_code=-100)
        finally:
            return request_item


def override_run_script_name(self, run_script_name: str) -> None:
    self.env_man.set_name_run_script_file(run_script_name)


class DictVariation(VariationBase, ServerRequest):
    def __init__(
            self,
            scenario_path: str,
            parameter_dict_list: List[dict],
            qoi: Union[str, List[str]],
            model: Command,
            scenario_runs=1,
            post_changes=PostScenarioChangesBase(apply_default=True),
            njobs_create_scenarios=1,
            output_path=None,
            output_folder=None,
            remove_output=False,
            env_remote=None,
    ) -> None:

        self.scenario_path = scenario_path
        self.remove_output = remove_output

        assert os.path.exists(scenario_path) and scenario_path.endswith(
            ".scenario"
        ), "Filepath must exist and the file has to end with .scenario"

        if env_remote is None:
            env = VadereEnvironmentManager.create_variation_env(
                basis_scenario=self.scenario_path,
                base_path=output_path,
                env_name=output_folder,
                handle_existing="ask_user_replace",
            )
            self.env_path = env.env_path
        else:
            self.env_path = env_remote.env_path
            self.remove_output = False  # Do not remove the folder because this is done with the remote procedure
            env = env_remote

        parameter_variation = UserDefinedSampling(parameter_dict_list)
        parameter_variation = parameter_variation.multiply_scenario_runs(
            scenario_runs=scenario_runs
        )

        super(DictVariation, self).__init__(
            env_man=env,
            parameter_variation=parameter_variation,
            model=model,
            qoi=qoi,
            post_changes=post_changes,
            njobs=njobs_create_scenarios,
            remove_output=remove_output,
        )


class SingleKeyVariation(DictVariation, ServerRequest):
    def __init__(
            self,
            scenario_path: str,
            key: str,
            values: np.ndarray,
            qoi: Union[str, List[str]],
            model: Command,
            scenario_runs=1,
            post_changes=PostScenarioChangesBase(apply_default=True),
            output_path=None,
            output_folder=None,
            remove_output=False,
            env_remote=None,
    ):
        self.key = key
        self.values = values

        simple_grid = [{key: v} for v in values]
        super(SingleKeyVariation, self).__init__(
            scenario_path=scenario_path,
            parameter_dict_list=simple_grid,
            qoi=qoi,
            model=model,
            scenario_runs=scenario_runs,
            post_changes=post_changes,
            output_folder=output_folder,
            output_path=output_path,
            remove_output=remove_output,
            env_remote=env_remote,
        )


class FolderExistScenarios(Request, ServerRequest):
    def __init__(
            self,
            path_scenario_folder,
            model,
            scenario_runs=1,
            output_path=None,
            output_folder=None,
            handle_existing="ask_user_replace",
    ):

        self.scenario_runs = scenario_runs
        assert os.path.exists(path_scenario_folder)
        self.path_scenario_folder = path_scenario_folder

        self.env_man = VadereEnvironmentManager.create_new_environment(
            base_path=output_path,
            env_name=output_folder,
            handle_existing=handle_existing,
        )

        request_item_list = list()

        for filename in os.listdir(os.path.abspath(path_scenario_folder)):
            file_base_name = os.path.basename(filename)

            if file_base_name.endswith(".scenario"):
                scenario_name = file_base_name.replace(".scenario", "")

                request_item = self._generate_request_items(
                    scenario_name=scenario_name, filename=filename
                )

                request_item_list += request_item

        super(FolderExistScenarios, self).__init__(
            request_item_list=request_item_list, model=model, qoi=None
        )
        ServerRequest.__init__(self)

    @classmethod
    def _remote_run(cls, remote_pickle_arg_path):

        kwargs = cls.open_arg_pickle(remote_pickle_arg_path)

        setup = cls(
            path_scenario_folder=kwargs["remote_folder_path"],
            model=kwargs["model"],
            output_folder=kwargs["remote_env_name"],
            handle_existing="write_in",
        )
        res = setup.run(kwargs["njobs"])
        cls.dump_result_pickle(res, kwargs["remote_pickle_res_path"])

    def _generate_request_items(self, scenario_name, filename):

        # generate request item for each scenario run
        scenario_request_items = list()
        for run in range(self.scenario_runs):
            item = RequestItem(
                parameter_id=scenario_name,
                run_id=run,
                scenario_path=os.path.join(self.path_scenario_folder, filename),
                base_path=self.env_man.env_path,
                output_folder="_".join(
                    [
                        scenario_name,
                        "output",
                        "" if self.scenario_runs == 1 else str(run),
                    ]
                ),
            )

            scenario_request_items.append(item)
        return scenario_request_items

    def remote(self, njobs=1):

        local_pickle_content = {"njobs": njobs}

        local_transfer_files = dict()
        for i, request in enumerate(self.request_item_list):
            local_transfer_files["scenario_path_{i}"] = request.scenario_path

        self._remote_ssh_logic(
            local_env_man=self.env_man,
            local_pickle_content=local_pickle_content,
            local_transfer_files=local_transfer_files,
            local_model_obj=self.model,
            class_name="FolderExistScenarios",
            transfer_output=True,
        )

    def run(self, njobs: int = 1):
        _, meta_info = super(FolderExistScenarios, self).run(njobs)
        return meta_info


class ProjectOutput(FolderExistScenarios):
    def __init__(self, project_path, model):

        if not os.path.exists(project_path):
            raise ValueError(f"project_path {project_path} odes not exist.")

        if not os.path.isfile(project_path) or not project_path.endswith(".project"):
            raise ValueError(
                f"project_path has to be the path to a Vadere project file (ending with .project)."
            )

        parent_path = parent_folder_clean(project_path)

        # This is by Vaderes convention:
        path_scenario_folder = os.path.join(parent_path, "scenarios")
        super(ProjectOutput, self).__init__(
            path_scenario_folder=path_scenario_folder,
            model=model,
            output_path=parent_path,
            output_folder="output",
        )


class SingleExistScenario(Request, ServerRequest):
    def __init__(
            self,
            path_scenario,
            qoi,
            model,
            scenario_runs=1,
            output_path=None,
            output_folder=None,
            handle_existing="ask_user_replace",
    ):

        self.path_scenario = os.path.abspath(path_scenario)
        assert os.path.exists(self.path_scenario) and self.path_scenario.endswith(
            ".scenario"
        )

        scenario_name = os.path.basename(path_scenario).replace(".scenario", "")

        self.env_man = VadereEnvironmentManager.create_new_environment(
            base_path=output_path,
            env_name=output_folder,
            handle_existing=handle_existing,
        )
        self.scenario_runs = scenario_runs

        if qoi is not None:
            if isinstance(qoi, (str, list)):
                with open(path_scenario, "r") as f:
                    basis_scenario = json.load(f)
                qoi = VadereQuantityOfInterest(
                    basis_scenario=basis_scenario, requested_files=qoi
                )
            else:
                raise ValueError("Invalid format of Quantity of Interest")

        request_item_list = self._generate_request_list(
            scenario_name=scenario_name, path_scenario=path_scenario
        )

        super(SingleExistScenario, self).__init__(
            request_item_list=request_item_list, model=model, qoi=qoi
        )
        ServerRequest.__init__(self)

    def _generate_request_list(self, scenario_name, path_scenario):

        if self.scenario_runs == 1:
            # No need to attach the run_id if there is only one run
            output_folder = lambda run_id: os.path.join(
                self.env_man.env_name, "vadere_output"
            )
        else:
            output_folder = lambda run_id: os.path.join(
                self.env_man.env_name,
                f"vadere_output_{str(run_id).zfill(len(str(run_id)))}",
            )

        request_item_list = list()
        for run_id in range(self.scenario_runs):
            request_item = RequestItem(
                parameter_id=scenario_name,
                run_id=run_id,
                scenario_path=path_scenario,
                base_path=self.env_man.base_path,
                output_folder=output_folder(run_id=run_id),
            )
            request_item_list.append(request_item)
        return request_item_list

    def run(self, njobs: int = 1):
        res = super(SingleExistScenario, self).run(njobs)
        return res

    @classmethod
    def _remote_run(cls, remote_pickle_arg_path):

        kwargs = cls.open_arg_pickle(remote_pickle_arg_path)

        setup = cls(
            path_scenario=kwargs["path_scenario"],
            qoi=kwargs["qoi"],
            model=kwargs["model"],
            scenario_runs=kwargs["scenario_runs"],
            output_path=None,
            output_folder=kwargs["remote_env_name"],
            handle_existing="write_in",
        )  # needs to write in because the environment already exists

        res = setup.run(njobs=kwargs["njobs"])
        cls.dump_result_pickle(res, kwargs["remote_pickle_res_path"])

    def remote(self, njobs=1):

        local_pickle_content = {
            "njobs": njobs,
            "qoi": self.qoi,
            "scenario_runs": self.scenario_runs,
        }
        local_transfer_files = {"path_scenario": self.path_scenario}

        self._remote_ssh_logic(
            local_env_man=self.env_man,
            local_pickle_content=local_pickle_content,
            local_transfer_files=local_transfer_files,
            local_model_obj=self.model,
            class_name="SingleExistScenario",
            transfer_output=True,
        )


# class CrownetVadereControlRequest(Request):
#     """
#         Request class for crownet based simulation with omnet and sumo.
#         Currently no qoi are supported. This Request only runs the simulation
#         and keeps the output for further processing
#     """
#
#     def __init__(self,
#                  env_man: AbstractEnvironmentManager,
#                  parameter_variation: ParameterVariationBase,
#                  model: Union[str, AbstractConsoleWrapper],
#                  njobs: int = 1
#                  ):
#         self.env_man = env_man
#         self.parameter_variation = parameter_variation
#         request_item_list = self.scenario_creation(njobs)
#         super().__init__(
#             request_item_list,
#             model,
#             qoi=None)
#
#     @classmethod
#     def create(cls,
#                ini_path: str,
#                config: str,
#                parameter_dict_list: List[dict],
#                output_path: str,
#                output_folder: str,
#                seed_config: Dict,
#                repeat: int = 1,
#                debug: bool = False,
#                ):
#
#         # fixme: extract user interaction from class method
#         # workaround using `create_new_environment` class method only for user interaction to clear existing
#         # environments if needed.
#         base_path, env_name = AbstractEnvironmentManager.handle_path_and_env_input(output_path, output_folder)
#         _ = CrownetVadereControlEnvironmentManager.create_new_environment(base_path, env_name,
#                                                                  handle_existing="ask_user_replace")
#
#         # build CrownetSumoEnvironmentManager and copy data. This version only copys *needed* files as the source
#         # enviroment (base_path) contains multiple big scenario setups that are not needed. See copy_data() for details.
#         env_man = CrownetVadereControlEnvironmentManager(
#             base_path=base_path,
#             env_name=env_name,
#             opp_config=config,
#             opp_basename=os.path.basename(ini_path),
#             debug=debug
#         )
#         env_man.copy_data(ini_path)
#
#         # create sampling. Do not add host name 'dummy' parameters. The will be set correclty in the run_script.py
#         sampling = CrownetVadereControlUserDefinedSampling(parameter_dict_list)
#         sampling.multiply_scenario_runs_using_seed(repeat, seed_config)
#
#         return cls(
#             env_man=env_man,
#             parameter_variation=sampling,
#             model=CrownetSumoWrapper()
#         )
#
#     def scenario_creation(self, njobs):
#
#         # todo: Sumo sampling currently not supported. Possible changes my occur in multiple files
#         scenario_creation = CrownetSumoCreation(self.env_man, self.parameter_variation)
#         request_item_list = scenario_creation.generate_scenarios(njobs)
#         return request_item_list
#
#     def _single_request(self, r_item: RequestItem) -> RequestItem:
#         """
#         build args for given request item. Quantity of intrest my given
#         and executed by the run_script.py for each item but results are
#         currently not aggregated by the CrownetSumoRequest
#         """
#
#         # ensure output path exists (deletes existing folder if present)
#         self._create_output_path(r_item.output_path)
#         if self.qoi is not None:
#             required_files = [k.filename for k in self.qoi.req_qois]
#         else:
#             required_files = []
#
#         # helper method in model class to create complex arguments for single run.
#         args = self.model.build_args(
#             env_man=self.env_man,
#             r_item=r_item,
#             required_files=required_files
#         )
#
#         return_code, required_time, output_on_error = self.model.run_simulation(
#             dirname=os.path.dirname(r_item.scenario_path),
#             start_file=self.env_man.run_file,
#             args=args
#         )
#
#         is_results = self._interpret_return_value(
#             return_code, r_item.parameter_id
#         )
#
#         result = None
#         if not is_results:
#             # something went wrong during run
#             if output_on_error is None:
#                 output_on_error = {
#                     "stdout": b"no output found",
#                     "stderr": b"no output found"
#                 }
#
#             filename_stdout = "stdout_on_error.txt"
#             filename_stderr = "stderr_on_error.txt"
#             self._write_console_output(
#                 output_on_error["stdout"], r_item.output_path, filename_stdout
#             )
#             self._write_console_output(
#                 output_on_error["stderr"], r_item.output_path, filename_stderr
#             )
#             result = None
#
#         r_item.add_qoi_result(result)
#         r_item.add_meta_info(required_time, return_code)
#
#         # todo: currently no output is deleted for manual processing
#         # if self.remove_output is True:
#         #     shutil.rmtree(dirname)
#         return r_item

class CrownetRequest(Request):
    """
    Request class for crownet based simulation with omnet and sumo.
    Currently no qoi are supported. This Request only runs the simulation
    and keeps the output for further processing
    """

    def __init__(self,
                 env_man: CrownetEnvironmentManager,
                 parameter_variation: ParameterVariationBase,
                 model: Command,
                 creator,   # callable
                 njobs: int = 1,
                 retries: int = 1,
                 rnd_hostname_suffix: str = "",
                 runscript_out: str|None = None
                 ):
        self.env_man = env_man
        self.parameter_variation = parameter_variation
        self._creator = creator
        self.rnd_hostname_suffix = rnd_hostname_suffix
        self.runscript_out = runscript_out
        request_item_list = self.scenario_creation(njobs)
        super().__init__(
            request_item_list,
            model,
            qoi=None,
            retries=retries)
        # todo create suqContext?
        self._models = {}
        self.write_context_files()
    

    def write_context_files(self):
        for r_item in self.request_item_list:
            par_id = r_item.parameter_id
            run_id = r_item.run_id
            _model: Command = deepcopy(self.model)
            dirname = os.path.join(
                self.env_man.get_env_outputfolder_path(),
                self.env_man.get_simulation_directory(par_id, run_id),
            )
            # Setup command arguments (defaults and fix values)
            _model.override_host_config(f"{os.path.basename(dirname)}{self.rnd_hostname_suffix}")
            _model.result_dir(r_item.output_path)
            _model.opp_argument("-f", os.path.basename(self.env_man.omnet_path_ini))  # todo..
            _model.opp_argument("-c", self.env_man.ini_config)
            _model.omnet_tag(self.env_man.communication_sim[1], override=False)
            _model.reuse_policy("remove_stopped", override=False)
            _model.cleanup_policy("keep_failed", override=False)


            if self.env_man.uses_sumo_mobility:
                _model.create_sumo_container()
                _model.sumo_tag(self.env_man.mobility_sim[1], override=False)
                _model.sumo_argument("bind", "0.0.0.0", override=False)
                _model.sumo_argument("port", "9999", override=False)

            if self.env_man.uses_vadere_mobility:
                _model.create_vadere_container()
                _model.vadere_tag(self.env_man.mobility_sim[1], override=False)
                # todo hard coded to 0.0.0.0
                # _model.vadere_argument("bind", "0.0.0.0", override=False)
                _model.v_traci_port(9998, override=False)

                _ini = self.env_man.omnet_ini_for_run(os.path.join(dirname, os.path.basename(self.env_man.omnet_path_ini)))
                _scenario, _sim = check_simulator(_ini) 
                _model.scenario_file(_scenario, override=False)

            _model.set_script(self.env_man.run_file)
            _model.write_context(os.path.join(dirname, "runContext.json"), dirname, r_item)
            self._models[(par_id, run_id)] = _model

    def scenario_creation(self, njobs):

        # todo: Sumo sampling currently not supported. Possible changes my occur in multiple files
        request_item_list = self._creator(self.env_man, self.parameter_variation, njobs)
        return request_item_list

    def _single_request(self, r_item: RequestItem) -> RequestItem:
        """
        build args for given request item. Quantity of intrest my given
        and executed by the run_script.py for each item but results are
        currently not aggregated by the CrownetSumoRequest
        """

        par_id = r_item.parameter_id
        run_id = r_item.run_id

        dirname = os.path.join(
            self.env_man.get_env_outputfolder_path(),
            self.env_man.get_simulation_directory(par_id, run_id),
        )
        print(f"run {par_id}_{run_id}")

        # ensure output path exists (deletes existing folder if present)
        self._create_output_path(r_item.output_path)
        if self.qoi is not None:
            required_files = [k.filename for k in self.qoi.req_qois]
        else:
            required_files = []

        output_on_error = None

        # access specific model for current par_id/run_id combination
        # runContext.json already created. 
        _model: Command = self._models[(par_id, run_id)]
        
        if self.runscript_out is not None:
            with open(os.path.join(r_item.output_path, self.runscript_out), "w", encoding="utf-8") as fd:
                return_code, required_time = _model.run(cwd=dirname, out=fd, err=fd)
        else:
            return_code, required_time = _model.run(cwd=dirname)

        is_results = self._interpret_return_value(
            return_code, r_item.parameter_id
        )

        result = None
        if not is_results:
            # something went wrong during run
            if output_on_error is None:
                output_on_error = {
                    "stdout": b"no output found",
                    "stderr": b"no output found"
                }

            filename_stdout = "stdout_on_error.txt"
            filename_stderr = "stderr_on_error.txt"
            self._write_console_output(
                output_on_error["stdout"], r_item.output_path, filename_stdout
            )
            self._write_console_output(
                output_on_error["stderr"], r_item.output_path, filename_stderr
            )
            result = None

        return_code = 0 # assume success allways
        r_item.add_qoi_result(result)
        r_item.add_meta_info(required_time, return_code)

        # todo: currently no output is deleted for manual processing
        # if self.remove_output is True:
        #     shutil.rmtree(dirname)

        return r_item


class OmnetRequest(Request):
    def __init__(self,
                 env_man: AbstractEnvironmentManager,
                 parameter_variation: ParameterVariationBase,
                 model: Command,
                 njobs: int = 1
                 ):
        self.env_man = env_man
        self.parameter_variation = parameter_variation
        request_item_list = self.scenario_creation(njobs)
        super().__init__(
            request_item_list,
            model,
            qoi=None)

    def scenario_creation(self, njobs):
        # todo: Sumo sampling currently not supported. Possible changes my occur in multiple files
        scenario_creation = CrownetCreation(self.env_man, self.parameter_variation)
        request_item_list = scenario_creation.generate_scenarios(njobs)
        return request_item_list


if __name__ == "__main__":
    pass
