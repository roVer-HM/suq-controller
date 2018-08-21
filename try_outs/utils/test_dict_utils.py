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


    def test_key_chaining(self):
        d = {"a": {"b": 1}, "b": 3}

        self.assertEqual(deep_dict_lookup(d, key="a|b", check_final_leaf=True, check_unique_key=True)[0], 1)
        self.assertEqual(deep_dict_lookup(d, key="a|b", check_final_leaf=False, check_unique_key=False)[0], 1)
        self.assertEqual(deep_dict_lookup(d, key="a|b", check_final_leaf=True, check_unique_key=False)[0], 1)
        self.assertEqual(deep_dict_lookup(d, key="a|b", check_final_leaf=False, check_unique_key=True)[0], 1)

        self.assertEqual(deep_dict_lookup(d, key="a|b", check_final_leaf=False, check_unique_key=True)[1], ["a", "b"])
        self.assertEqual(deep_dict_lookup(d, key="a|b", check_final_leaf=False, check_unique_key=False)[1], ["a", "b"])
        self.assertEqual(deep_dict_lookup(d, key="a|b", check_final_leaf=True, check_unique_key=True)[1], ["a", "b"])
        self.assertEqual(deep_dict_lookup(d, key="a|b", check_final_leaf=False, check_unique_key=True)[1], ["a", "b"])

        with self.assertRaises(ValueError):
            deep_dict_lookup(d, key="b", check_unique_key=True)

        with self.assertRaises(ValueError):
            deep_dict_lookup(d, key="c")

        d1 = {"a": {"b": {"c": 1}}, "b": {"c": 2}, "c": 3}

        self.assertEqual(deep_dict_lookup(d1, key="a|b|c")[0], 1)
        self.assertEqual(deep_dict_lookup(d1, key="a|b|c")[1], ["a", "b", "c"])

        self.assertEqual(deep_dict_lookup(d1, key="b|c")[0], 2)
        self.assertEqual(deep_dict_lookup(d1, key="b|c")[1], ["b", "c"])

        self.assertEqual(deep_dict_lookup(d1, key="|b|c")[0], 2)

        self.assertEqual(deep_dict_lookup(d1, key="|c")[0], 3)  # special case: root|key, only works for the very first

        with self.assertRaises(ValueError):
            deep_dict_lookup(d1, key="c")

        d2 = {"a": {"b": {"c": 1}}, "b": {"c": {"d": 1}}, "c": {"a": 1}, "e": {"a": {"b": {"g": 3}}}}

        self.assertEqual(deep_dict_lookup(d2, "c|a"), (1, ["c", "a"]))
        self.assertEqual(deep_dict_lookup(d2, "|a", check_final_leaf=False), ({'b': {'c': 1}}, ["a"]))

        self.assertEqual(deep_dict_lookup(d2, "b", check_unique_key=False, check_final_leaf=False), ({"c": 1}, ["a", "b"]))
        self.assertEqual(deep_dict_lookup(d2, "|b", check_unique_key=False, check_final_leaf=False), ({"c": {"d": 1}}, ["b"]))

        self.assertEqual(deep_dict_lookup(d2, "d"), (1, ["b", "c", "d"]))
        self.assertEqual(deep_dict_lookup(d2, "b|c", check_final_leaf=False), ({"d": 1}, ["b", "c"]))
        self.assertEqual(deep_dict_lookup(d2, "|b|c", check_final_leaf=False), ({"d": 1}, ["b", "c"]))
        self.assertEqual(deep_dict_lookup(d2, "a|b|c"), (1, ["a", "b", "c"]))
        self.assertEqual(deep_dict_lookup(d2, "b|c|d"), (1, ["b", "c", "d"]))
        self.assertEqual(deep_dict_lookup(d2, "|b|c|d"), (1, ["b", "c", "d"]))

        self.assertEqual(deep_dict_lookup(d2, "g"), (3, ["e", "a", "b", "g"]))
        self.assertEqual(deep_dict_lookup(d2, "|g"), (3, ["e", "a", "b", "g"]))

        with self.assertRaises(ValueError):
            deep_dict_lookup(d2, "b")

        with self.assertRaises(ValueError):
            deep_dict_lookup(d2, "c")

        d3 = {"a": {"b": {"c": {"d": 1}}}, "b": {"d": 2}}

        with self.assertRaises(ValueError):
            deep_dict_lookup(d3, "d")

        self.assertEqual(deep_dict_lookup(d3, "c|d"), (1, ["a", "b", "c", "d"]))
        self.assertEqual(deep_dict_lookup(d3, "b|d"), (2, ["b", "d"]))
        self.assertEqual(deep_dict_lookup(d3, "a|b|d"), (1, ["a", "b", "c", "d"]))
        self.assertEqual(deep_dict_lookup(d3, "a|b|c|d"), (1, ["a", "b", "c", "d"]))


if __name__ == '__main__':
    DictUtilTests().test_trivial()
    DictUtilTests().test_nested()
    DictUtilTests().test_check_integrity_and_leaf()
    DictUtilTests().test_key_chaining()
    unittest.main()