#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import unittest

from try_outs.utils.dict_utils import *

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class DictUtilTests(unittest.TestCase):

    def test_trivial(self):
        d1 = {"a": 1}
        self.assertEqual(deep_dict_lookup(d1, "a", check_unique_key=True)[0], 1)
        self.assertEqual(deep_dict_lookup(d1, "a", check_unique_key=False)[0], 1)

        self.assertEqual(deep_dict_lookup(d1, "a", check_unique_key=True)[1], ["a"])
        self.assertEqual(deep_dict_lookup(d1, "a", check_unique_key=False)[1], ["a"])

        with self.assertRaises(ValueError):
            deep_dict_lookup(d1, "b")

    def test_nested(self):
        d2 = {"a": {"b": {"c": 1}}}
        self.assertEqual(deep_dict_lookup(d2, "c", check_unique_key=True)[0], 1)
        self.assertEqual(deep_dict_lookup(d2, "c", check_unique_key=False)[0], 1)

        self.assertEqual(deep_dict_lookup(d2, "c", check_unique_key=True)[1], ["a", "b", "c"])
        self.assertEqual(deep_dict_lookup(d2, "c", check_unique_key=False)[1], ["a", "b", "c"])

        self.assertEqual(deep_dict_lookup(d2, "b", check_final_leaf=False, check_unique_key=True)[0], {"c": 1})
        self.assertEqual(deep_dict_lookup(d2, "b", check_final_leaf=False, check_unique_key=False)[0], {"c": 1})

        self.assertEqual(deep_dict_lookup(d2, "b", check_final_leaf=False, check_unique_key=False)[1], ["a", "b"])
        self.assertEqual(deep_dict_lookup(d2, "b", check_final_leaf=False, check_unique_key=False)[1], ["a", "b"])

    def test_deeper_nested(self):
        d1 = {"a": {"b": {"c": 1}}, "b": {"c": 2}, "c": 3}

        self.assertEqual(deep_dict_lookup(d1, "c", check_final_leaf=False, check_unique_key=False)[0], 1)
        self.assertEqual(deep_dict_lookup(d1, "c", check_final_leaf=True, check_unique_key=False)[0], 1)

        with self.assertRaises(ValueError):
            deep_dict_lookup(d1, "c", check_final_leaf=True, check_unique_key=True)

        # TODO: also get deep_dict_lookup to allow keys with "|" syntax, which would be called recursively...



    def test_check_integrity_and_leaf(self):

        d3 = {"a": {"b": {"a": 1}}}
        d4 = {"a": {"b": {"c": 1}}}

        self.assertEqual(deep_dict_lookup(d3, "a", check_final_leaf=False, check_unique_key=False)[0], {"b": {"a": 1}})
        self.assertEqual(deep_dict_lookup(d3, "b", check_final_leaf=False, check_unique_key=False)[1], ["a", "b"])

        with self.assertRaises(ValueError):
            deep_dict_lookup(d3, "a", check_unique_key=True)

        self.assertEqual(deep_dict_lookup(d4, "c", check_final_leaf=True, check_unique_key=False)[0], 1)

        with self.assertRaises(ValueError):
            deep_dict_lookup(d4, "b", check_final_leaf=True, check_unique_key=False)


if __name__ == '__main__':
    DictUtilTests().test_trivial()
    DictUtilTests().test_nested()
    DictUtilTests().test_check_integrity_and_leaf()
    unittest.main()
