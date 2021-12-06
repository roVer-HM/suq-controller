import random
import copy
from typing import Dict, Any, List


class SeedManager:
    def __init__(self, par_variations: List[Dict[str, Any]],
                 seed_config: Dict[str, str] = {"vadere": "random", "omnet": "random"}, rep_count: int = 1):
        """SeedManager class for crownet based simulation

        Attributes:
        -----
        par_variations: List[Dict[str, Any]]
            the parameter variation that needs to be seeded
        seed_config:  Dict[str, str]
            seed configuration (default {"vadere": "random", "omnet": "random"})
        rep_count: int
            repetition count determines how many seed different seed configuration are set per variation
        """
        self.parameter_variations = par_variations
        self.repetition_count = rep_count
        self.omnet_seed_range = range(1, 255)
        self.vadere_seed_range = range(1, 100000)
        self.seed_config = seed_config
        if rep_count == 0:
            raise ValueError("rep_count of 0 is not supported")

    def _set_seed(self, variation: Dict[str, Any], vadere_seed: int, omnet_seed: int):
        # todo: if sumo gets implemented, add new sumo seed

        # seed already set
        if self._seed_parameter_exists(variation):
            raise ValueError("Seed already set in the given dictionary.")

        # vadere seed
        if "vadere" in self.seed_config:
            if self.seed_config["vadere"] == "fixed":
                self._add_vadere_seed_fixed(variation)
            else:
                if "omnet" in self.parameter_variations:
                    self._add_vadere_seed_random(variation, vadere_seed)
                else:
                    self._add_vadere_seed_random_only(variation, 12345)  # todo mario: fixme after finish

        # omnet seed
        if "omnet" in self.seed_config:
            if self.seed_config["omnet"] == "fixed":
                self._add_omnet_seed_fixed(variation)
            else:
                self._add_omnet_seed_random(variation, omnet_seed)
        # sumo seed
        if "sumo" in self.seed_config:
            if self.seed_config["sumo"] == "fixed":
                self._add_sumo_seed_fixed(variation)
            else:
                self._add_sumo_seed_random(variation, -1)

    def _seed_parameter_exists(self, parameter_variations: Dict[str, Any]) -> bool:
        vadere_seed_keys = ["attributesSimulation.useFixedSeed"]
        omnet_seed_keys = ["*.traci.launcher.useVadereSeed", "*.traci.launcher.seed", "seed-set"]
        omnet_key = "omnet"
        vadere_key = "vadere"
        omnet_exists = any([key in parameter_variations[omnet_key] for key in omnet_seed_keys]) \
            if omnet_key in parameter_variations else False
        vadere_exists = any([key in parameter_variations[vadere_key] for key in vadere_seed_keys]) \
            if vadere_key in parameter_variations else False
        return any([omnet_exists, vadere_exists])

    def _add_vadere_seed_fixed(self, parameter_variations: Dict[str, Any]) -> "SeedManager":
        # use fixed seed defined in scenario file
        parameter_variations["omnet"]["*.traci.launcher.useVadereSeed"] = "true"
        parameter_variations["vadere"]["attributesSimulation.useFixedSeed"] = True
        return self

    def _add_vadere_seed_random(self, parameter_variations: Dict[str, Any], seed: int) -> "SeedManager":
        # use random seed in vadere provided from omnet ini file
        parameter_variations["omnet"]["*.traci.launcher.useVadereSeed"] = "false"
        parameter_variations["omnet"]["*.traci.launcher.seed"] = str(seed)
        return self

    def _add_vadere_seed_random_only(self, parameter_variations: Dict[str, Any], seed: int) -> "SeedManager":
        # use random seed in vadere provided from omnet ini file
        parameter_variations["vadere"]["fixedSeed"] = seed
        return self

    def _add_omnet_seed_fixed(self, parameter_variations: Dict[str, Any]):
        # use fixed seed defined in omnet ini file
        pass

    def _add_omnet_seed_random(self, parameter_variations: Dict[str, Any], seed: int) -> "SeedManager":
        # use random seed for omnet
        parameter_variations["omnet"]["seed-set"] = str(seed)
        return self

    def _add_sumo_seed_fixed(self, parameter_variation: Dict[str, Any]) -> "SeedManager":
        # not implemented
        raise NotImplementedError("sumo seeds are not implemented.")

    def _add_sumo_seed_random(self, parameter_variation: Dict[str, Any], seed: int) -> "SeedManager":
        # not implemented
        raise NotImplementedError("sumo seeds are not implemented.")

    def get_new_seed_variation(self) -> List[
        Dict[str, Any]]:
        """
                Generates a new seed variation.

                Returns
                -------
                out : List[Dict[str, Any]]
                    List of seeded variants.

                Examples
                --------
                >>> SeedManager(par_variations=[variation_1, variation_2], rep_count=2).get_new_seed_variation()
                [variation_1_seed_1,
                variation_1_seed_2,
                variation_2_seed_1,
                variation_2_seed_2]
                >>> SeedManager(par_variations=[variation_1], rep_count=4).get_new_seed_variation()
                [variation_1_seed_1,
                variation_1_seed_2,
                variation_1_seed_3,
                variation_1_seed_4]
                >>> SeedManager(par_variations=[variation_1, variation_2]).get_new_seed_variation()
                [variation_1_seed_1,
                variation_1_seed_2]

        """
        ret: List[Dict[str, Any]] = []
        vadere_samples = random.sample(self.vadere_seed_range, self.repetition_count)
        omnet_samples = random.sample(self.omnet_seed_range, self.repetition_count)
        for parameter_variation in self.parameter_variations:
            for rep in range(self.repetition_count):
                copied_element = copy.deepcopy(parameter_variation)
                self._set_seed(variation=copied_element, omnet_seed=omnet_samples[rep], vadere_seed=vadere_samples[rep])
                ret.append(copied_element)
        return ret

    # @staticmethod
    # def check_seed_config(seed_config: Dict):
    #     if set(seed_config.keys()) != {"vadere", "omnet"}:
    #         raise ValueError(
    #             f"Dictionary keys must be: omnet, vadere or sumo. Got {set(seed_config.keys())}."
    #         )

    # def multiply_scenario_runs_using_seed(
    #         self, scenario_runs: Union[int, List[int]], seed_config: Dict
    # ):
    #
    #     super().multiply_scenario_runs(scenario_runs)
    #     return self
