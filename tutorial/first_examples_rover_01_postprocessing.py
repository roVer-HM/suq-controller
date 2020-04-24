from suqc import read_from_existing_output
from tutorial.imports import *
import matplotlib.pyplot as plt
from numpy import diff
from scipy.signal import find_peaks

if __name__ == "__main__":

    # read existing data and store them in dataframe
    output_folder = "simple"
    qoi = "DegreeInformed.txt"
    env_path = os.path.join(path2tutorial,output_folder)
    df, meta_df = read_from_existing_output( env_path= env_path , qoi_filename = qoi, parentfolder_level = 5 )

    analysis_path = os.path.join(env_path,"analysis")
    shutil.rmtree(analysis_path, ignore_errors=True)
    os.makedirs(analysis_path)

    dt = 0.4
    df["timeStep"] = dt * df["timeStep"]

    qoi = pd.DataFrame(meta_df.iloc[:, 0])
    qoi = qoi.rename( columns = { "('Parameter', 'vadere', 'sources.[id==3001].distributionParameters')" : "inter_arrival_t_sec"})

    number_peaks, evolution_times = list(), list()
    stats = pd.DataFrame()

    for simulation in meta_df.index:
        df_r = df.loc[simulation]
        time = df_r.iloc[:,0]
        percentage_informed = df_r.iloc[:,3]
        derivative = diff(percentage_informed) / dt
        percentage_informed = percentage_informed[0:-1]
        time = time[0:-1]

        index_start_time = np.argwhere(percentage_informed == 0.0)[-1]+1
        index_end_time = np.argwhere(percentage_informed >= 0.95)[0]+1

        start_time = dt*index_start_time
        end_time = dt*index_end_time

        evolution_time = end_time - start_time
        t_i = np.round(evolution_time[0], 5)

        my_title = f'Parameter: mean inter-arrival-time t_m = {qoi.loc[simulation, "inter_arrival_t_sec"][1:5]}s \n QoI: time 95% informed t_i = {t_i}s'
        my_title_short = f'Simulation_{simulation}__mean_time_{qoi.loc[simulation, "inter_arrival_t_sec"][1:5]}'.replace(",","_").replace(".","_")
        plt.title(my_title)

        border_up = np.infty * np.ones(len(percentage_informed)).T
        border_low = dt* percentage_informed.values

        peaks, _ = find_peaks(derivative, distance=15, height = (border_low, border_up ) )
        plt.plot(time, 100*percentage_informed)
        plt.plot(time, 100*derivative)
        plt.plot(peaks*dt, 100*derivative[peaks], "x")

        plt.xlabel("Time [s]")
        plt.ylabel("Percentage of pedestrians informed [%]")
        plt.legend(('Information degree', 'Information degree - Derivative'),loc="center right")

        plt.savefig(os.path.join(analysis_path, my_title_short + "_all.png"))
        plt.show()

        number_peaks.append(peaks.size)
        peak_time = dt * peaks[0]

        if peak_time < start_time or peak_time > end_time:
            print(f"Please check simulation {simulation}")

        evolution_times.append(evolution_time)

        tol = 4
        plt.plot(time[index_start_time[0] - tol:index_end_time[0] + tol],
                 100 * percentage_informed[index_start_time[0] - tol:index_end_time[0] + tol])

        for yc, c in zip([0, 95], ['m','m']):
            plt.axhline(y=yc, c=c)

        for xc, c in zip([start_time[0], end_time[0]], ['r', 'r']):
            plt.axvline(x=xc, c=c)

        plt.arrow(start_time[0], 50, evolution_time[0], 0, head_width=2, head_length=0.2,color='k', length_includes_head=True)
        plt.arrow(end_time[0], 50, -evolution_time[0], 0, head_width=2, head_length=0.2,color='k', length_includes_head=True)
        plt.text(start_time[0]+0.375*evolution_time[0], 53, f"t_i = {t_i}s")

        plt.xlabel("Time [s]")
        plt.ylabel("Percentage of pedestrians informed [%]")
        plt.legend(('Information degree', '0% und 95% borders'),loc="lower right",bbox_to_anchor=(0.9, 0.2))

        plt.title(my_title)
        plt.savefig( os.path.join(analysis_path, my_title_short + ".png"))
        plt.show()

        stat = pd.Series.describe( df_r.iloc[150:-1,2] )
        stats = pd.concat( [stats, pd.DataFrame(stat).transpose()] )

    stats = stats.reset_index()

    qoi = qoi.droplevel(["run_id"]).reset_index()
    qoi = qoi.assign(time_all_informed = evolution_times)
    qoi = qoi.assign(number_of_peaks = number_peaks)
    qoi = pd.concat ( [qoi,stats], axis=1 )



    plt.plot([ float(item[1:4]) for item in  qoi["inter_arrival_t_sec"]], qoi["time_all_informed"],marker="o")
    plt.xlabel(f"Parameter: mean inter-arrival-time [s]")
    plt.title("Time to inform 95% of pedestrians [s]")
    plt.ylabel("QoI: time [s]")
    plt.savefig(os.path.join(analysis_path, f"MAIN_result_Information_time_over_inter_arrival_time.png"))
    plt.show()

    plot_items = ["mean", "max", "75%"]

    for x in plot_items:
        plt.plot(qoi[x], qoi["time_all_informed"],marker="o")
        plt.xlabel(f"Number of pedestrians over time: {x} value [-]")
        plt.title("Time to inform 95% of pedestrians [s]")
        plt.ylabel("QoI: time [s]")
        plt.savefig(os.path.join(analysis_path, f"Time_to_inform_95percent_summary_para_used_{x}.png"))
        plt.show()

    print("postprocessing")