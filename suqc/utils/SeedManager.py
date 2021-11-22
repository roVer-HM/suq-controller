import random
import copy
from typing import Dict, Any, List


# class SeedManager(ParameterVariationBase):
# todo Mario:
#  - Die Dictionaries in der Liste werden je nachdem wie groß anzahl der repetition ist dupliziert
#  - len(list) == 2 mit rep 3 -> len(list)  == 6
#  - SeedManager().get_varations = Liste(mitSeeds und repetition)
#  - SeedManager().apply_vadere_seed() - Liste(mitSeeds und repetition)
#  - SeedManager().apply_vadere_seed().get_variations() - Liste(mitSeeds und repetition)
#  - SeedManager().get_variations() - Liste(Repetition)
#  - getRepetition() -> Liste mit kopierten Dictionaries
#  - getVariation() -> Liste mit einfachen Dictionaries
#  - addVadereSeed(seeed: int)
#  -  rep = anzahl Variationen mit Random seed
#  - verschiedene Variationen können selben selben seed haben
# run  rep  seed
# 0 0 5
# 0 1 4
# 0 2 3
# 1 0 5
# 1 1 4
# 1 2 3

class SeedManager:
    def __init__(self, par_variations: List[Dict[str, Any]], rep_count: int = 1):
        self.parameter_variations = par_variations
        self.repetition_count = rep_count
        self.omnet_seed_range = range(1, 255)
        self.Vadere_seed_range = range(1, 100000)
        # erzeuge liste je nach repcount (self.parameter_variations)
        self.parameter_repetition = None

    def _create_repeated_seed_variations(self, variations: List[Dict[str, Any]], repetitions: int) -> List[
        Dict[str, Any]]:
        ret: List[Dict[str, Any]] = []
        for parameter_variation in variations:
            for rep in range(repetitions):
                ret.append(copy.deepcopy(parameter_variation))
        # random.sample(range(1, 100), len(self.variations)) # number of repetition => als seed länger, da andere parameter kombi selber seed
        # omnet-seeds 1-255
        # vadere-seeds 1-100000
        return ret

    def _seed_parameter_exists(self, parameter_variations: Dict[str, Any]) -> bool:
        vadere_seed_keys = ["attributesSimulation.useFixedSeed"]
        omnet_seed_keys = ["*.traci.launcher.useVadereSeed", "*.traci.launcher.seed", "seed-set"]
        omnet_key = "omnet"
        vadere_key = "vadere"
        omnet_exists = any([key in parameter_variations[omnet_key] for key in omnet_seed_keys])
        vadere_exists = any([key in parameter_variations[vadere_key] for key in vadere_seed_keys])
        return any([omnet_exists, vadere_exists])

    def add_vadere_seed_fixed(self, parameter_variations: Dict[str, Any]) -> "SeedManager":
        if self._seed_parameter_exists(parameter_variations):
            raise ValueError("Seed already set in the given dictionary.")
        parameter_variations["omnet"]["*.traci.launcher.useVadereSeed"] = "true"
        parameter_variations["vadere"]["attributesSimulation.useFixedSeed"] = True
        return self

    def add_vadere_seed_random(self, parameter_variations: Dict[str, Any], seed: int) -> "SeedManager":
        if self._seed_parameter_exists(parameter_variations):
            raise ValueError("Seed already set in the given dictionary.")
        # use random seed in vadere provided from omnet ini file
        parameter_variations["omnet"]["*.traci.launcher.useVadereSeed"] = "false"
        parameter_variations["omnet"]["*.traci.launcher.seed"] = seed
        return self

    def add_omnet_seed_fixed(self, parameter_variations: Dict[str, Any], fixed_seed=True):
        # not implemented
        pass  # use fixed seed defined in omnet ini file

    def add_omnet_seed_random(self, parameter_variations: Dict[str, Any], seed: int) -> "SeedManager":
        if self._seed_parameter_exists(parameter_variations):
            raise ValueError("Seed already set in the given dictionary.")
        # use random seed for omnet
        # seed = str(random.randint(1, 255))
        parameter_variations["omnet"]["seed-set"] = seed
        return self

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
