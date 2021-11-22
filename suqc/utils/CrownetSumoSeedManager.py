from typing import List, Dict, Union

from suqc.utils.SeedManager import SeedManager


class CrownetSumoSeedManager(SeedManager):

    def __init__(self, points: List[dict]):
        super().__init__(points)

    @staticmethod
    def check_seed_config(seed_config: Dict):
        if set(seed_config.keys()) != {"sumo", "omnet"}:
            raise ValueError(
                f"Dictionary keys must be: omnet, sumo. Got {set(seed_config.keys())}."
            )

    def apply_sumo_seed(self, seed_config: Dict):
        # todo changes my occur in multiple files
        pass

    def multiply_scenario_runs_using_seed(self, scenario_runs: Union[int, List[int]], seed_config: Dict):
        super().multiply_scenario_runs(scenario_runs)

        if seed_config is not None:
            self.check_seed_config(seed_config)
            # omnet seed
            self.add_omnet_seed_fixed(seed_config)
            # sumo seed
            self.apply_sumo_seed(seed_config)

            self._points = self.points.sort_index(axis=1)

        return self