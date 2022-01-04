import unittest
from unittest import mock
import copy

from suqc.CommandBuilder.interfaces.CommandArguments import CommandArguments

from suqc.utils.SeedManager.OmnetSeedManager import OmnetSeedManager


class TestCommandArguments(unittest.TestCase):
    c_args = CommandArguments({"key_1": "value_1", "key_2": "value_2"})

    def test__init__(self):
        empty_args = CommandArguments()
        empty_args.store = dict()

        dict_arg = CommandArguments({"key": "value"})
        dict_arg.store = {"key", "value"}

    def test__getitem__(self):
        self.assertEqual(self.c_args["key_1"], "value_1")
        self.assertEqual(self.c_args["key_2"], "value_2")

    def test__setitem__(self):
        c_args_copy = copy.deepcopy(self.c_args)
        c_args_copy["key_3"] = "value_3"
        self.assertEqual(c_args_copy["key_3"], "value_3")

    def test__delitem__(self):
        c_args_copy = copy.deepcopy(self.c_args)
        self.assertTrue(len(c_args_copy) == 2)
        del c_args_copy["key_2"]
        self.assertTrue(len(c_args_copy) == 1)

    def test_set(self):
        c_args_copy = copy.deepcopy(self.c_args)
        c_args_copy.set(key="key_1", value="value_42", override=False)
        self.assertEqual(c_args_copy["key_1"], "value_1")

        c_args_copy.set(key="key_1", value="value_42", override=True)
        self.assertEqual(c_args_copy["key_1"], "value_42")

        c_args_copy.set(key="key_3", value="value_3", override=False)
        self.assertEqual(c_args_copy["key_3"], "value_3")

    def test__iter__(self):
        iter_args = CommandArguments({"key_1": "value_1", "bool_flag": None, "list_item": ["1", "2", "3"]})
        listed = list(iter_args)
        self.assertEqual(listed[0], "key_1")
        self.assertEqual(listed[1], "value_1")
        self.assertEqual(listed[2], "bool_flag")
        self.assertEqual(listed[3], "list_item")
        self.assertEqual(listed[4], "1")
        self.assertEqual(listed[5], "2")
        self.assertEqual(listed[6], "3")

    def test__len__(self):
        self.assertEqual(len(self.c_args), len(self.c_args.store))

    def test__str__(self):
        iter_args = CommandArguments({"key_1": "value_1", "bool_flag": None, "list_item": ["1", "2", "3"]})
        stringed = str(iter_args)
        self.assertEqual(stringed, f"key_1 value_1 bool_flag None list_item 1 2 3")

if __name__ == '__main__':
    unittest.main()
