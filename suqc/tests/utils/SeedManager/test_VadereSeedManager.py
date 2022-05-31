import random
import unittest
from unittest import mock
import copy

from suqc.utils.SeedManager.VadereSeedManager import VadereSeedManager


class TestVadereSeedManager(unittest.TestCase):
    empty_variation = {'vadere': {}, 'omnet': {}}
    seed_manager = VadereSeedManager([empty_variation])

    def test__init__(self):
        empty_args = VadereSeedManager(par_variations=[])
        self.assertEqual(empty_args.vadere_seed_range, range(1, 100000))
        self.assertEqual(empty_args.parameter_variations, [])
        self.assertEqual(empty_args.vadere_fixed, True)
        self.assertEqual(empty_args.repetition_count, 1)

        set_args = VadereSeedManager(par_variations=[self.empty_variation],
                                     vadere_fixed=False,
                                     rep_count=5)
        self.assertEqual(set_args.vadere_seed_range, range(1, 100000))
        self.assertEqual(set_args.parameter_variations, [self.empty_variation])
        self.assertEqual(set_args.vadere_fixed, False)
        self.assertEqual(set_args.repetition_count, 5)

        # raise warning with repetition count of 0
        with self.assertRaises(ValueError) as context:
            VadereSeedManager(par_variations=[], rep_count=0)
        self.assertEqual(str(context.exception), "rep_count of 0 is not supported")

    @mock.patch('suqc.utils.SeedManager.VadereSeedManager.VadereSeedManager._add_vadere_seed_fixed')
    @mock.patch('suqc.utils.SeedManager.VadereSeedManager.VadereSeedManager._add_vadere_seed_random')
    def test_set_seed(self,
                      vadere_random_mock: mock.MagicMock,
                      vadere_fixed_mock: mock.MagicMock):
        var_copy = copy.deepcopy(self.empty_variation)
        vadere_seed = 1

        def reset_mocks():
            vadere_random_mock.reset_mock()
            vadere_fixed_mock.reset_mock()
            var_copy = copy.deepcopy(self.empty_variation)

        # vadere fixed
        s_fixed_fixed = VadereSeedManager(par_variations=[self.empty_variation],
                                          vadere_fixed=True)
        s_fixed_fixed._set_seed(variation=var_copy, vadere_seed=vadere_seed)
        self.assertEqual(vadere_fixed_mock.call_count, 1)
        self.assertEqual(vadere_random_mock.call_count, 0)
        vadere_fixed_mock.assert_called_once_with(var_copy)
        reset_mocks()

        # vadere random
        s_fixed_random = VadereSeedManager(par_variations=[self.empty_variation],
                                           vadere_fixed=False)
        s_fixed_random._set_seed(variation=var_copy, vadere_seed=vadere_seed)
        self.assertEqual(vadere_fixed_mock.call_count, 0)
        self.assertEqual(vadere_random_mock.call_count, 1)
        vadere_random_mock.assert_called_once_with(var_copy, vadere_seed)

    def test_add_vadere_seed_fixed(self):
        self.seed_manager._add_vadere_seed_fixed({})
        self.assertTrue("No logic in function" == "No logic in function")

    def test_add_vadere_seed_random(self):
        empty_copy = copy.deepcopy(self.empty_variation)
        seed = 1
        self.seed_manager._add_vadere_seed_random(empty_copy, seed)
        self.assertTrue("vadere" in empty_copy)
        self.assertTrue("fixedSeed" in empty_copy["vadere"])
        self.assertEqual(empty_copy["vadere"]["fixedSeed"], seed)

    @mock.patch('random.sample')
    def test_get_new_seed_variation(self, sample_mock: mock.MagicMock):
        sample_mock.return_value = [1, 2, 3, 4]
        t1_seed_manager = VadereSeedManager(par_variations=[self.empty_variation],
                                            vadere_fixed=True,
                                            rep_count=2)
        t1_seed_manager._rnd = random # replace custom random object with global random generator for test
        results = t1_seed_manager.get_new_seed_variation()
        self.assertTrue(len(results) == 2)

        t2_seed_manager = VadereSeedManager(par_variations=[self.empty_variation, self.empty_variation],
                                            vadere_fixed=False,
                                            rep_count=2)
        t2_seed_manager._rnd = random # replace custom random object with global random generator for test
        results = t2_seed_manager.get_new_seed_variation()
        self.assertTrue(len(results) == 4)
        self.assertEqual(results[0]["vadere"]["fixedSeed"], 1)
        self.assertEqual(results[1]["vadere"]["fixedSeed"], 2)
        self.assertEqual(results[2]["vadere"]["fixedSeed"], 1)
        self.assertEqual(results[3]["vadere"]["fixedSeed"], 2)



if __name__ == '__main__':
    unittest.main()
