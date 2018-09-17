#!/usr/bin/env python3 

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import unittest

from suqc.server.remote import *
from suqc.qoi import PedestrianEvacuationTimeProcessor

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class TestRemote(unittest.TestCase):

    def test_small_corner_environment(self):
        env_man = EnvironmentManager("corner")
        par_var = FullGridSampling(env_man)
        par_var.add_dict_grid({"speedDistributionStandardDeviation": [0.0]})
        qoi = PedestrianEvacuationTimeProcessor(env_man)

        with ServerConnection() as sc:
            server_sim = ServerSimulation(sc)
            server_sim.run(env_man, par_var, qoi)


def main():
    TestRemote().test_small_corner_environment()
    unittest.main()


if __name__ == "__main__":
    main()
