from typing import Union, List

import pandas as pd
import os

from suqc import (
    CoupledEnvironmentManager,
    CoupledScenarioCreation,
    ParameterVariationBase,
    VariationBase,
)


def recover_sim(
    samples_to_repeat: Union[tuple, List[tuple]],
    env=None,
    meta_info_file="metainfo.pkl",
    env_info_file = "info_env_manager.txt",
):

    if isinstance(samples_to_repeat, list):
        if (
            all(
                isinstance(sampl_to_repeat, tuple)
                for sampl_to_repeat in samples_to_repeat
            )
            is False
        ):
            raise ValueError(
                f"Expect a list of tuples like (id,run_id). Got {samples_to_repeat}."
            )

    if isinstance(samples_to_repeat, tuple):
        samples_to_repeat = [samples_to_repeat]

    if os.path.splitext(meta_info_file)[1] != ".pkl":
        raise ValueError(f"meta_info_file must be a *.pkl file. Got {meta_info_file}.")

    df = pd.read_pickle(os.path.join(env, meta_info_file))
    df.columns = pd.MultiIndex.from_tuples(df.columns.tolist())
    df = df.iloc[:, df.columns.get_level_values(0) == "Parameter"]
    df = df.loc[samples_to_repeat, :]

    env = CoupledEnvironmentManager.create_variation_env_from_info_file(
       os.path.join(env,env_info_file)
    )

    par = ParameterVariationBase()
    par._add_df_points(df)

    cou = CoupledScenarioCreation(env_man=env, parameter_variation=par,)
    cou.generate_scenarios(1)

    print("Please start the simulations manually.")


if __name__ == "__main__":

    recover_sim(
        samples_to_repeat=(1, 0),
        env="/home/christina/repos/suq-controller/tutorial/test_me",
    )
