from abc import ABC
from typing import Dict, Any, List


class SeedManager(ABC):
    def __init__(self, par_variations: List[Dict[str, Any]], rep_count: int = 1):
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
        if rep_count == 0:
            raise ValueError("rep_count of 0 is not supported")
