import pandas as pd

from suqc import (
    CoupledEnvironmentManager,
    CoupledScenarioCreation,
    ParameterVariationBase,
    VariationBase,
)


def recover_sim():
    # TODO create single simulation from data
    df = pd.read_csv(
        "/home/christina/repos/suq-controller/tutorial/test_me/metainfo.csv",
    )

    cols = []
    for col in df.columns:
        col = col.replace("/","")
        col = col.replace("'", "")
        col = col.replace('"', "")
        col = col.replace('(', "")
        col = col.replace(')', "")
        col = col.split(",")
        cols.append(tuple(col))

    df.columns = pd.MultiIndex.from_tuples(cols)

    # df = pd.read_pickle(
    #     "/home/christina/repos/suq-controller/tutorial/test_me/metainfo.pkl"
    # )

    env = CoupledEnvironmentManager.create_variation_env_from_info_file(
        "/home/christina/repos/suq-controller/tutorial/test_me/info_env_manager.txt"
    )

    par = ParameterVariationBase()
    par._add_df_points(df)

    cou = CoupledScenarioCreation(
        env_man=env,
        parameter_variation=par,
    )
    #cou.generate_scenarios(1)

    # var = VariationBase(
    #     env_man=env,
    #     parameter_variation=par,
    #     model="Coupled",
    #     qoi=["a"],
    #     remove_output=False,
    # )

    print("finished")


if __name__ == "__main__":
    recover_sim()
