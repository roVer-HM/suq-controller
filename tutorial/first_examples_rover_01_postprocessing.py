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
    df = read_from_existing_output( env_path= env_path , qoi_filename = qoi, parentfolder_level = 5 )

    simulation_runs = df.index.get_duplicates().to_list()

    dt = 0.4
    df["timeStep"] = dt * df["timeStep"]

    number_peaks, evolution_times = list(), list()

    for simulation in simulation_runs:
        df_r = df.loc[simulation]
        time = df_r.iloc[:,0]
        percentage_informed = df_r.iloc[:,3]
        derivative = diff(percentage_informed) / dt
        percentage_informed = percentage_informed[0:-1]
        time = time[0:-1]

        border_up = np.infty * np.ones(len(percentage_informed)).T
        border_low = dt* percentage_informed.values

        peaks, _ = find_peaks(derivative, distance=15, height = (border_low, border_up ) )
        plt.plot(time, percentage_informed)
        plt.plot(time, derivative)
        plt.plot(peaks*dt, derivative[peaks], "x")
        plt.show()

        number_peaks.append(peaks.size)

        peak_time = dt*peaks[0]
        start_time = dt *  np.argwhere(percentage_informed == 0.0)[-1]
        end_time = dt * np.argwhere(percentage_informed == 1.0)[0]

        evolution_time = end_time - start_time

        if peak_time < start_time or peak_time > end_time:
            print("error")
        else:
            print("ok")

        evolution_times.append(evolution_time)


        #plt.plot(time[145:160], percentage_informed[145:160])
        #plt.plot(time[145:160], derivative[145:160])
        #plt.show()



    print("postprocessing")