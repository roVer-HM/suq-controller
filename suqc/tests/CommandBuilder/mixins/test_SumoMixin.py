import unittest

from suqc.CommandBuilder.mixins.SumoMixin import SumoMixin

from suqc.CommandBuilder.interfaces.CommandArguments import CommandArguments


class BaseMixinClass(SumoMixin):
    _arguments = CommandArguments()


class TestSumoMixin(unittest.TestCase):
    mixin = BaseMixinClass()

    def test_create_sumo_container(self):
        expected = None
        self.mixin.create_sumo_container()
        self.assertEqual(self.mixin._arguments["--crate-sumo-container"], expected)

    def test_sumo_tag(self):
        expected = "any_tag"
        self.mixin.sumo_tag(expected)
        self.assertEqual(self.mixin._arguments["--sumo-tag"], expected)

    def test_sumo_argument(self):
        expected_key = "any_key"
        expected_value = "any_value"
        self.mixin.sumo_argument(expected_key, expected_value)
        self.assertEqual(self.mixin._arguments[f"--sumo.{expected_key}"], expected_value)
