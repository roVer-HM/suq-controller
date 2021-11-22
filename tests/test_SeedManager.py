import unittest
from unittest import mock
import copy

from suqc.utils.SeedManager import SeedManager


class TestStringMethods(unittest.TestCase):
    """
    TODO: New Tests after SeedManager is updated
    """
    seed_manager = SeedManager()
    no_seed_variation = {'vadere': {}, 'omnet': {}}
    fixed_seed_variation = {'vadere': {'attributesSimulation.useFixedSeed': True},
                            'omnet': {'*.traci.launcher.useVadereSeed': "true"}}
    random_seed_variation = {'vadere': {'attributesSimulation.useFixedSeed': True},
                             'omnet': {'*.traci.launcher.useVadereSeed': "false",
                                       '*.traci.launcher.seed': [57455, 35466]}}

    def test_seed_parameter_exists(self):
        self.assertFalse(self.seed_manager._seed_parameter_exists(self.no_seed_variation))
        self.assertTrue(self.seed_manager._seed_parameter_exists(self.fixed_seed_variation))
        self.assertTrue(self.seed_manager._seed_parameter_exists(self.random_seed_variation))

    @mock.patch('random.randint')
    def test_add_vadere_seed(self, randint_mock: mock.MagicMock):
        # fixed seed
        par_variation = copy.deepcopy(self.no_seed_variation)
        self.seed_manager.add_vadere_seed(parameter_variations=par_variation, fixed_seed=True)
        self.assertTrue('attributesSimulation.useFixedSeed' in par_variation["vadere"])
        self.assertTrue('*.traci.launcher.useVadereSeed' in par_variation["omnet"])

        with self.assertRaises(ValueError) as context_manager:
            self.seed_manager.add_vadere_seed(parameter_variations=par_variation, fixed_seed=True)
        self.assertEqual(str(context_manager.exception), "Seed already set in the given dictionary.")

        # random seed
        randint_mock.return_value = 42
        par_variation = copy.deepcopy(self.no_seed_variation)
        self.seed_manager.add_vadere_seed(parameter_variations=par_variation, fixed_seed=False)
        self.assertTrue('*.traci.launcher.useVadereSeed' in par_variation["omnet"])
        self.assertTrue('*.traci.launcher.seed' in par_variation["omnet"])
        self.assertEqual(par_variation["omnet"]['*.traci.launcher.seed'], str(randint_mock.return_value))

        with self.assertRaises(ValueError) as context_manager:
            self.seed_manager.add_vadere_seed(parameter_variations=par_variation, fixed_seed=False)
        self.assertEqual(str(context_manager.exception), "Seed already set in the given dictionary.")

    @mock.patch('random.randint')
    def test_apply_omnet_seed(self, randint_mock: mock.MagicMock):
        # fixed seed (not implemented path)
        par_variation = copy.deepcopy(self.no_seed_variation)
        self.seed_manager.add_omnet_seed_fixed(parameter_variations=par_variation, fixed_seed=True)
        self.assertEqual(par_variation, self.no_seed_variation)

        # random seed
        randint_mock.return_value = 42
        par_variation = copy.deepcopy(self.no_seed_variation)
        self.seed_manager.add_omnet_seed_fixed(parameter_variations=par_variation, fixed_seed=False)
        self.assertTrue('seed-set' in par_variation["omnet"])
        self.assertEqual(par_variation["omnet"]['seed-set'], str(randint_mock.return_value))

        with self.assertRaises(ValueError) as context_manager:
            self.seed_manager.add_omnet_seed_fixed(parameter_variations=par_variation, fixed_seed=False)
        self.assertEqual(str(context_manager.exception), "Seed already set in the given dictionary.")


if __name__ == '__main__':
    unittest.main()
