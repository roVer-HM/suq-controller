#!/usr/bin/env python3

import sys
import warnings

import matplotlib.pyplot as plt
from numpy import diff
from scipy.signal import find_peaks

import roveranalyzer.oppanalyzer.wlan80211 as w80211
from roveranalyzer.oppanalyzer.utils import RoverBuilder
from roveranalyzer.uitls.path import PathHelper
from suqc.parameter.parameter import (DependentParameter, Parameter,
                                      RoverSampling,
                                      RoverSamplingFullFactorial)
from tutorial.imports import *

# This is just to make sure that the systems path is set up correctly, to have correct imports, it can be ignored:
sys.path.append(os.path.abspath("."))
sys.path.append(os.path.abspath(".."))

run_local = True
###############################################################################################################
# Usecase: Set yourself the parameters you want to change. Do this by defining a list of dictionaries with the
# corresponding parameter. Again, the Vadere output is deleted after all scenarios run.


def preprocessing_and_simulation_run(
    par_var, path2ini, output_folder, qoi, repitions=1
):

    path2model = "Coupled"

    setup = CoupledDictVariation(
        ini_path=path2ini,
        scenario_name="simple_detour_100x177_miat1.25.scenario",
        parameter_dict_list=par_var,
        qoi=qoi,
        model=path2model,
        scenario_runs=repitions,
        post_changes=PostScenarioChangesBase(apply_default=True),
        output_path=path2tutorial,
        output_folder=output_folder,
        remove_output=False,
        remove_omnet_files=True,
    )

    if run_local:
        par_var, data = setup.run(
            1
        )  # -1 indicates to use all cores available to parallelize the scenarios
        # to do: allow -1 for rover containers
    else:
        par_var, data = setup.remote(-1)

    print("simulation runs: finished")


def postprocessing(output_folder, qoi):

    # read existing data and store them in dataframe
    env_path = os.path.join(path2tutorial, output_folder)
    df, meta_df = read_from_existing_output(
        env_path=env_path, qoi_filename=qoi, parentfolder_level=5
    )

    analysis_path = os.path.join(env_path, "analysis")
    shutil.rmtree(analysis_path, ignore_errors=True)
    os.makedirs(analysis_path)

    dt = 0.4
    df["timeStep"] = dt * df["timeStep"]

    qoi = meta_df
    qoi2 = pd.DataFrame(qoi.iloc[:,0])
    qoi2 = qoi2.rename(
        columns={
            "('Parameter', 'vadere', 'sources.[id==3001].distributionParameters')": "interArrivalTimeSecs"
        }
    )
    qoi2["interArrivalTimeSecs"] = qoi2["interArrivalTimeSecs"].str.replace("]","")
    qoi2["interArrivalTimeSecs"] = qoi2["interArrivalTimeSecs"].str.replace("[", "").astype(float)
    qoi = pd.concat([qoi, qoi2], axis=1)


    number_peaks, evolution_times = list(), list()
    stats = pd.DataFrame()

    for simulation in meta_df.index:

        df_r = df.loc[simulation]
        time = df_r.iloc[:, 0]
        percentage_informed = df_r.iloc[:, 3]

        derivative = diff(percentage_informed) / dt
        percentage_informed = percentage_informed[0:-1]
        time = time[0:-1]

        try:

            index_start_time = np.where(percentage_informed == 0.0)[0][-1] + 1
            index_end_time = np.where(percentage_informed >= 0.95)[0][0] + 1

            start_time = dt * index_start_time
            end_time = dt * index_end_time

            evolution_time = end_time - start_time

            tol = 4

        except:

            index_start_time = np.where(percentage_informed == 0.0)[0][-1] + 1
            index_end_time = len(percentage_informed) - 1

            start_time = dt * index_start_time
            end_time = dt * index_end_time

            tol = 0

            evolution_time = np.NaN

        t_i = np.round(evolution_time, 5)

        my_title = f'Parameter: mean inter-arrival-time t_m = {qoi.loc[simulation, "interArrivalTimeSecs"]}s \n QoI: time 95% informed t_i = {t_i}s'
        my_title_short = f'Simulation_{simulation}__mean_time_{qoi.loc[simulation, "interArrivalTimeSecs"]}'.replace(
            ",", "_"
        ).replace(
            ".", "_"
        )
        plt.title(my_title)

        border_up = np.infty * np.ones(len(percentage_informed)).T
        border_low = dt * percentage_informed.values

        peaks, _ = find_peaks(derivative, distance=15, height=(border_low, border_up))
        plt.plot(time, 100 * percentage_informed)
        plt.plot(time, 100 * derivative)
        plt.plot(peaks * dt, 100 * derivative[peaks], "x")

        plt.xlabel("Time [s]")
        plt.ylabel("Percentage of pedestrians informed [%]")
        plt.legend(
            ("Information degree", "Information degree - Derivative"),
            loc="center right",
        )

        #plt.savefig(os.path.join(analysis_path, my_title_short + "_all.png"))
        plt.show()

        number_peaks.append(peaks.size)
        try:
            peak_time = dt * peaks[0]

            if peak_time < start_time or peak_time > end_time:
                pass
                #print(f"Please check simulation {simulation}")

        except:
            print("failed")

        evolution_times.append(evolution_time)

        plt.plot(
            time[index_start_time - tol : index_end_time + tol],
            100 * percentage_informed[index_start_time - tol : index_end_time + tol],
        )

        for yc, c in zip([0, 95], ["m", "m"]):
            plt.axhline(y=yc, c=c)

        for xc, c in zip([start_time, end_time], ["r", "r"]):
            plt.axvline(x=xc, c=c)

        plt.arrow(
            start_time,
            50,
            evolution_time,
            0,
            head_width=2,
            head_length=0.2,
            color="k",
            length_includes_head=True,
        )
        plt.arrow(
            end_time,
            50,
            -evolution_time,
            0,
            head_width=2,
            head_length=0.2,
            color="k",
            length_includes_head=True,
        )
        plt.text(start_time + 0.375 * evolution_time, 53, f"t_i = {t_i}s")

        plt.xlabel("Time [s]")
        plt.ylabel("Percentage of pedestrians informed [%]")
        plt.legend(
            ("Information degree", "0% und 95% borders"),
            loc="lower right",
            bbox_to_anchor=(0.9, 0.2),
        )

        plt.title(my_title)
        #plt.savefig(os.path.join(analysis_path, my_title_short + ".png"))
        plt.show()

        stat = pd.Series.describe(df_r.iloc[index_start_time:index_end_time, 2])
        stats = pd.concat([stats, pd.DataFrame(stat).transpose()])

    stats = stats.set_index(qoi.index)

    qoi = qoi.assign(time95informed=evolution_times)
    qoi = qoi.assign(numberOfPeaks=number_peaks)
    qoi = pd.concat([qoi, stats], axis=1)
    qoi.to_csv(os.path.join(analysis_path, "qoi_summary.csv"), sep = ";")

    plt.plot(
        qoi["interArrivalTimeSecs"],
        qoi["time95informed"],
        marker="o",
    )
    plt.xlabel(f"Parameter: mean inter-arrival-time [s]")
    plt.title("Time to inform 95% of pedestrians [s]")
    plt.ylabel("QoI: time [s]")
    plt.savefig(
        os.path.join(
            analysis_path, f"MAIN_result_Information_time_over_inter_arrival_time.png"
        )
    )
    plt.show()

    plot_items = ["mean", "max", "75%"]

    for x in plot_items:
        plt.plot(qoi[x], qoi["time95informed"], marker="o")
        plt.xlabel(f"Number of pedestrians over time: {x} value [-]")
        plt.title("Time to inform 95% of pedestrians [s]")
        plt.ylabel("QoI: time [s]")
        plt.savefig(
            os.path.join(
                analysis_path, f"Time_to_inform_95percent_summary_para_used_{x}.png"
            )
        )
        plt.show()

    print("postprocessing: finished")


def mac_analysis(base_dir, fig_title, vec_input, prefix, out_input=None):
    builder = RoverBuilder(
        path=PathHelper(base_dir),
        analysis_name=f"{prefix}mac",
        analysis_dir="analysis.d",
        hdf_store_name="analysis.h5",
    )
    builder.set_scave_filter('module("*.hostMobile[*].*.mac")')
    builder.set_scave_input_path(vec_input)
    if out_input is not None:
        _log_file = builder.root.join(out_input)
    else:
        _log_file = ""
    w80211.create_mac_pkt_drop_figures(
        builder=builder,
        log_file=_log_file,
        figure_title=fig_title,
        figure_prefix=prefix,
        hdf_key=f"/df/{prefix}mac_pkt_drop_ts",
        show_fig=True,
    )


def fp_traffic_no__obstacle_yes__seed_none():

    # define roVer simulation
    path2ini = os.path.join(
        os.environ["ROVER_MAIN"], "rover/simulations/simple_detoure_suqc/omnetpp.ini"
    )  # use this ini-file

    output_folder = os.path.join(
        path2tutorial,
        sys._getframe().f_code.co_name,
    )
    qoi = "DegreeInformed.txt"  # qoi

    # create sampling for rover - needs to be outsourced into Marions repo
    # example omnet:  Parameter("*.station[0].mobility.initialX", unit="m", simulator="omnet", range=[200, 201])
    parameter = [
        Parameter(
            name="number_of_agents_mean",
            simulator="dummy",
            range=np.log10([25,30]).tolist(),
            stages=10,
        )
    ]

    dependent_parameters = [
        DependentParameter(
            name="sources.[id==3001].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3002].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3003].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)] ",
        ),
        DependentParameter(
            name="sources.[id==3004].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sim-time-limit", simulator="omnet", equation='= "180s"'
        ),
        DependentParameter(
            name="*.station[0].app[0].incidentTime",
            simulator="omnet",
            equation='= "100s"',
        ),
        DependentParameter(
            name="*.radioMedium.obstacleLoss.typename",
            simulator="omnet",
            equation='= "IdealObstacleLoss"',
        ),
        DependentParameter(
            name="*.manager.useVadereSeed",
            simulator="omnet",
            equation='= "true"',
        )
    ]

    reps = [100, 100, 75, 75, 50, 50, 25, 25, 10, 10]
    reps = 2
    par_var = RoverSamplingFullFactorial(
        parameters=parameter, parameters_dependent=dependent_parameters
    ).get_sampling()
    preprocessing_and_simulation_run(
        par_var, path2ini, output_folder, qoi, repitions=reps
    )
    postprocessing(output_folder, qoi)


def fp_traffic_no__obstacle_yes__seed_set():

    # define roVer simulation
    path2ini = os.path.join(
        os.environ["ROVER_MAIN"], "rover/simulations/simple_detoure_suqc/omnetpp.ini"
    )  # use this ini-file

    output_folder = os.path.join(
        path2tutorial,
        sys._getframe(  ).f_code.co_name,
    )


    qoi = "DegreeInformed.txt"  # qoi

    # create sampling for rover - needs to be outsourced into Marions repo
    # example omnet:  Parameter("*.station[0].mobility.initialX", unit="m", simulator="omnet", range=[200, 201])
    parameter = [
        Parameter(
            name="number_of_agents_mean",
            simulator="dummy",
            range=np.log10([25,30]).tolist(),
            stages=10,
        )
    ]

    dependent_parameters = [
        DependentParameter(
            name="sources.[id==3001].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3002].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3003].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)] ",
        ),
        DependentParameter(
            name="sources.[id==3004].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sim-time-limit", simulator="omnet", equation='= "180s"'
        ),
        DependentParameter(
            name="*.station[0].app[0].incidentTime",
            simulator="omnet",
            equation='= "100s"',
        ),
        DependentParameter(
            name="*.radioMedium.obstacleLoss.typename",
            simulator="omnet",
            equation='= "IdealObstacleLoss"',
        ),
        DependentParameter(
            name="*.manager.useVadereSeed",
            simulator="omnet",
            equation='= "false"',
        )

    ]

    reps = 1
    par_var = RoverSamplingFullFactorial(
        parameters=parameter, parameters_dependent=dependent_parameters
    ).get_sampling()
    preprocessing_and_simulation_run(
        par_var, path2ini, output_folder, qoi, repitions=reps
    )
    postprocessing(output_folder, qoi)


def fp_traffic_no__obstacle_no__seed_set():

    # define roVer simulation
    path2ini = os.path.join(
        os.environ["ROVER_MAIN"], "rover/simulations/simple_detoure_suqc/omnetpp.ini"
    )  # use this ini-file

    output_folder = os.path.join(
        path2tutorial,
        sys._getframe().f_code.co_name,
    )


    qoi = "DegreeInformed.txt"  # qoi

    # create sampling for rover - needs to be outsourced into Marions repo
    # example omnet:  Parameter("*.station[0].mobility.initialX", unit="m", simulator="omnet", range=[200, 201])
    parameter = [
        Parameter(
            name="number_of_agents_mean",
            simulator="dummy",
            range=np.log10([25,30]).tolist(),
            stages=10,
        )
    ]

    dependent_parameters = [
        DependentParameter(
            name="sources.[id==3001].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3002].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3003].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)] ",
        ),
        DependentParameter(
            name="sources.[id==3004].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sim-time-limit", simulator="omnet", equation='= "180s"'
        ),
        DependentParameter(
            name="*.station[0].app[0].incidentTime",
            simulator="omnet",
            equation='= "100s"',
        ),
        DependentParameter(
            name="*.radioMedium.obstacleLoss.typename",
            simulator="omnet",
            equation='= ""',
        ),
        DependentParameter(
            name="*.manager.useVadereSeed",
            simulator="omnet",
            equation='= "false"',
        )

    ]

    reps = 1
    par_var = RoverSamplingFullFactorial(
        parameters=parameter, parameters_dependent=dependent_parameters
    ).get_sampling()
    preprocessing_and_simulation_run(
        par_var, path2ini, output_folder, qoi, repitions=reps
    )
    postprocessing(output_folder, qoi)


def fp_traffic_yes__obstacle_yes__seed_set():

    # define roVer simulation
    # define roVer simulation
    path2ini = os.path.join(
        os.environ["ROVER_MAIN"],
        "rover/simulations/simple_detoure_suqc_traffic/omnetpp.ini",
    )  # use this ini-file

    output_folder = os.path.join(
        path2tutorial,
        sys._getframe().f_code.co_name,
    )
    qoi = "DegreeInformed.txt"  # qoi

    # create sampling for rover - needs to be outsourced into Marions repo
    # example omnet:  Parameter("*.station[0].mobility.initialX", unit="m", simulator="omnet", range=[200, 201])
    parameter = [
        Parameter(
            name="number_of_agents_mean",
            simulator="dummy",
            range=np.log10([25,30]).tolist(),
            stages=10,
        ),
        Parameter(
            name="*.hostMobile[*].app[1].messageLength",
            simulator="omnet",
            unit="B",
            stages=[500, 5000, 50000],
        ),
    ]



    dependent_parameters = [
        DependentParameter(
            name="sources.[id==3001].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3002].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3003].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)] ",
        ),
        DependentParameter(
            name="sources.[id==3004].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sim-time-limit", simulator="omnet", equation='= "180s"'
        ),
        DependentParameter(
            name="*.station[0].app[0].incidentTime",
            simulator="omnet",
            equation='= "100s"',
        ),
        DependentParameter(
            name="*.radioMedium.obstacleLoss.typename",
            simulator="omnet",
            equation='= "IdealObstacleLoss"',
        ),
        DependentParameter(
            name="*.manager.useVadereSeed",
            simulator="omnet",
            equation='= "false"',
        )
    ]

    reps = 1
    par_var = RoverSamplingFullFactorial(
        parameters=parameter, parameters_dependent=dependent_parameters
    ).get_sampling()
    preprocessing_and_simulation_run(
        par_var, path2ini, output_folder, qoi, repitions=reps
    )
    postprocessing(output_folder, qoi)


def fp_traffic_yes__obstacle_no__seed_set():

    # define roVer simulation
    # define roVer simulation
    path2ini = os.path.join(
        os.environ["ROVER_MAIN"],
        "rover/simulations/simple_detoure_suqc_traffic/omnetpp.ini",
    )  # use this ini-file

    output_folder = os.path.join(
        path2tutorial,
        sys._getframe().f_code.co_name,
    )
    qoi = "DegreeInformed.txt"  # qoi

    # create sampling for rover - needs to be outsourced into Marions repo
    # example omnet:  Parameter("*.station[0].mobility.initialX", unit="m", simulator="omnet", range=[200, 201])
    parameter = [
        Parameter(
            name="number_of_agents_mean",
            simulator="dummy",
            range=np.log10([25,30]).tolist(),
            stages=10,
        ),
        Parameter(
            name="*.hostMobile[*].app[1].messageLength",
            simulator="omnet",
            unit="B",
            stages=[500, 5000, 50000],
        ),
    ]



    dependent_parameters = [
        DependentParameter(
            name="sources.[id==3001].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3002].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sources.[id==3003].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)] ",
        ),
        DependentParameter(
            name="sources.[id==3004].distributionParameters",
            simulator="vadere",
            equation=" = [1000/(10**number_of_agents_mean)]",
        ),
        DependentParameter(
            name="sim-time-limit", simulator="omnet", equation='= "180s"'
        ),
        DependentParameter(
            name="*.station[0].app[0].incidentTime",
            simulator="omnet",
            equation='= "100s"',
        ),
        DependentParameter(
            name="*.radioMedium.obstacleLoss.typename",
            simulator="omnet",
            equation='= ""',
        ),
        DependentParameter(
            name="*.manager.useVadereSeed",
            simulator="omnet",
            equation='= "false"',
        )
    ]

    reps = 1
    par_var = RoverSamplingFullFactorial(
        parameters=parameter, parameters_dependent=dependent_parameters
    ).get_sampling()
    preprocessing_and_simulation_run(
        par_var, path2ini, output_folder, qoi, repitions=reps
    )
    postprocessing(output_folder, qoi)



if __name__ == "__main__":

    os.environ["ROVER_MAIN"] = "/home/christina/repos/rover-main"
    warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

    fp_traffic_no__obstacle_no__seed_set()
    fp_traffic_no__obstacle_yes__seed_none()
    fp_traffic_no__obstacle_yes__seed_set()
    fp_traffic_yes__obstacle_no__seed_set()
    fp_traffic_yes__obstacle_yes__seed_set()

