import random
import unittest
from unittest import mock
import copy

from suqc.utils.SeedManager.OmnetSeedManager import OmnetSeedManager


class TestOmnetSeedManager(unittest.TestCase):
    empty_variation = {'vadere': {}, 'omnet': {}}
    seed_manager = OmnetSeedManager([empty_variation])

    def test__init__(self):
        empty_args = OmnetSeedManager(par_variations=[])
        self.assertEqual(empty_args.omnet_seed_range, range(1, 255))
        self.assertEqual(empty_args.vadere_seed_range, range(1, 100000))
        self.assertEqual(empty_args.parameter_variations, [])
        self.assertEqual(empty_args.omnet_fixed, True)
        self.assertEqual(empty_args.vadere_fixed, True)
        self.assertEqual(empty_args.repetition_count, 1)

        set_args = OmnetSeedManager(par_variations=[self.empty_variation],
                                    omnet_fixed=False,
                                    vadere_fixed=False,
                                    rep_count=5)
        self.assertEqual(set_args.omnet_seed_range, range(1, 255))
        self.assertEqual(set_args.vadere_seed_range, range(1, 100000))
        self.assertEqual(set_args.parameter_variations, [self.empty_variation])
        self.assertEqual(set_args.omnet_fixed, False)
        self.assertEqual(set_args.vadere_fixed, False)
        self.assertEqual(set_args.repetition_count, 5)

        # raise warning with repetition count of 0
        with self.assertRaises(ValueError) as context:
            OmnetSeedManager(par_variations=[], rep_count=0)
        self.assertEqual(str(context.exception), "rep_count of 0 is not supported")

    @mock.patch('suqc.utils.SeedManager.OmnetSeedManager.OmnetSeedManager._add_vadere_seed_fixed')
    @mock.patch('suqc.utils.SeedManager.OmnetSeedManager.OmnetSeedManager._add_vadere_seed_random')
    @mock.patch('suqc.utils.SeedManager.OmnetSeedManager.OmnetSeedManager._add_omnet_seed_fixed')
    @mock.patch('suqc.utils.SeedManager.OmnetSeedManager.OmnetSeedManager._add_omnet_seed_random')
    def test_set_seed(self,
                      omnet_random_mock: mock.MagicMock,
                      omnet_fixed_mock: mock.MagicMock,
                      vadere_random_mock: mock.MagicMock,
                      vadere_fixed_mock: mock.MagicMock):
        var_copy = copy.deepcopy(self.empty_variation)
        vadere_seed = 1
        omnet_seed = 2

        def reset_mocks():
            omnet_random_mock.reset_mock()
            omnet_fixed_mock.reset_mock()
            vadere_random_mock.reset_mock()
            vadere_fixed_mock.reset_mock()
            var_copy = copy.deepcopy(self.empty_variation)

        # vadere fixed, omnet fixed
        s_fixed_fixed = OmnetSeedManager(par_variations=[self.empty_variation],
                                         vadere_fixed=True,
                                         omnet_fixed=True)
        s_fixed_fixed._set_seed(variation=var_copy, vadere_seed=vadere_seed, omnet_seed=omnet_seed)
        self.assertEqual(vadere_random_mock.call_count, 0)
        self.assertEqual(vadere_fixed_mock.call_count, 1)
        self.assertEqual(omnet_random_mock.call_count, 0)
        self.assertEqual(omnet_fixed_mock.call_count, 1)
        vadere_fixed_mock.assert_called_once_with(var_copy)
        omnet_fixed_mock.assert_called_once_with(var_copy)
        reset_mocks()

        # vadere fixed, omnet random
        s_fixed_random = OmnetSeedManager(par_variations=[self.empty_variation],
                                          vadere_fixed=True,
                                          omnet_fixed=False)
        s_fixed_random._set_seed(variation=var_copy, vadere_seed=vadere_seed, omnet_seed=omnet_seed)
        self.assertEqual(vadere_random_mock.call_count, 0)
        self.assertEqual(vadere_fixed_mock.call_count, 1)
        self.assertEqual(omnet_random_mock.call_count, 1)
        self.assertEqual(omnet_fixed_mock.call_count, 0)
        vadere_fixed_mock.assert_called_once_with(var_copy)
        omnet_random_mock.assert_called_once_with(var_copy, omnet_seed)
        reset_mocks()

        # vadere random, omnet fixed
        s_random_fixed = OmnetSeedManager(par_variations=[self.empty_variation],
                                          vadere_fixed=False,
                                          omnet_fixed=True)
        s_random_fixed._set_seed(variation=var_copy, vadere_seed=vadere_seed, omnet_seed=omnet_seed)
        self.assertEqual(vadere_random_mock.call_count, 1)
        self.assertEqual(vadere_fixed_mock.call_count, 0)
        self.assertEqual(omnet_random_mock.call_count, 0)
        self.assertEqual(omnet_fixed_mock.call_count, 1)
        vadere_random_mock.assert_called_once_with(var_copy, vadere_seed)
        omnet_fixed_mock.assert_called_once_with(var_copy)
        reset_mocks()

        # vadere random, omnet random
        s_random_random = OmnetSeedManager(par_variations=[self.empty_variation],
                                           vadere_fixed=False,
                                           omnet_fixed=False)
        s_random_random._set_seed(variation=var_copy, vadere_seed=vadere_seed, omnet_seed=omnet_seed)
        self.assertEqual(vadere_random_mock.call_count, 1)
        self.assertEqual(vadere_fixed_mock.call_count, 0)
        self.assertEqual(omnet_random_mock.call_count, 1)
        self.assertEqual(omnet_fixed_mock.call_count, 0)
        vadere_random_mock.assert_called_once_with(var_copy, vadere_seed)
        omnet_random_mock.assert_called_once_with(var_copy, omnet_seed)

    def test_add_vadere_seed_fixed(self):
        empty_copy = copy.deepcopy(self.empty_variation)
        self.seed_manager._add_vadere_seed_fixed(empty_copy)
        self.assertTrue("*.traci.launcher.useVadereSeed" in empty_copy["omnet"])
        self.assertTrue("attributesSimulation.useFixedSeed" in empty_copy["vadere"])
        self.assertEqual(empty_copy["omnet"]["*.traci.launcher.useVadereSeed"], "true")
        self.assertEqual(empty_copy["vadere"]["attributesSimulation.useFixedSeed"], True)

    def test_add_vadere_seed_random(self):
        empty_copy = copy.deepcopy(self.empty_variation)
        seed = '1'
        self.seed_manager._add_vadere_seed_random(empty_copy, seed)
        self.assertTrue("*.traci.launcher.useVadereSeed" in empty_copy["omnet"])
        self.assertTrue("*.traci.launcher.seed" in empty_copy["omnet"])
        self.assertEqual(empty_copy["omnet"]["*.traci.launcher.useVadereSeed"], "false")
        self.assertEqual(empty_copy["omnet"]["*.traci.launcher.seed"], seed)

    def test_add_omnet_seed_fixed(self):
        self.seed_manager._add_omnet_seed_fixed({})
        self.assertTrue("No logic in function" == "No logic in function")

    def test_add_omnet_seed_random(self):
        empty_copy = copy.deepcopy(self.empty_variation)
        seed = '1'
        self.seed_manager._add_omnet_seed_random(empty_copy, seed)
        self.assertTrue("seed-set" in empty_copy["omnet"])
        self.assertEqual(empty_copy["omnet"]["seed-set"], seed)

    @mock.patch('random.sample')
    def test_get_new_seed_variation(self, sample_mock: mock.MagicMock):
        sample_mock.return_value = ['1', '2']
        t1_seed_manager = OmnetSeedManager(par_variations=[self.empty_variation],
                                           omnet_fixed=False,
                                           vadere_fixed=False,
                                           rep_count=2)
        t1_seed_manager._rnd = random # replace custom random object with global random generator for test
        results = t1_seed_manager.get_new_seed_variation()
        self.assertTrue(len(results) == 2)
        self.assertEqual(results[0]["omnet"]["*.traci.launcher.useVadereSeed"], 'false')
        self.assertEqual(results[0]["omnet"]["*.traci.launcher.seed"], sample_mock.return_value[0])
        self.assertEqual(results[1]["omnet"]["*.traci.launcher.useVadereSeed"], 'false')
        self.assertEqual(results[1]["omnet"]["*.traci.launcher.seed"], sample_mock.return_value[1])

        t2_seed_manager = OmnetSeedManager(par_variations=[self.empty_variation, self.empty_variation],
                                           omnet_fixed=False,
                                           vadere_fixed=True,
                                           rep_count=2)
        t2_seed_manager._rnd = random # replace custom random object with global random generator for test
        results = t2_seed_manager.get_new_seed_variation()
        self.assertTrue(len(results) == 4)
        self.assertEqual(results[0]["omnet"]["*.traci.launcher.useVadereSeed"], 'true')
        self.assertEqual(results[0]["omnet"]["seed-set"], sample_mock.return_value[0])
        self.assertEqual(results[0]["vadere"]["attributesSimulation.useFixedSeed"], True)

        self.assertEqual(results[1]["omnet"]["*.traci.launcher.useVadereSeed"], 'true')
        self.assertEqual(results[1]["omnet"]["seed-set"], sample_mock.return_value[1])
        self.assertEqual(results[1]["vadere"]["attributesSimulation.useFixedSeed"], True)

        self.assertEqual(results[2]["omnet"]["*.traci.launcher.useVadereSeed"], 'true')
        self.assertEqual(results[2]["omnet"]["seed-set"], sample_mock.return_value[0])
        self.assertEqual(results[2]["vadere"]["attributesSimulation.useFixedSeed"], True)

        self.assertEqual(results[3]["omnet"]["*.traci.launcher.useVadereSeed"], 'true')
        self.assertEqual(results[3]["omnet"]["seed-set"], sample_mock.return_value[1])
        self.assertEqual(results[3]["vadere"]["attributesSimulation.useFixedSeed"], True)


if __name__ == '__main__':
    unittest.main()
