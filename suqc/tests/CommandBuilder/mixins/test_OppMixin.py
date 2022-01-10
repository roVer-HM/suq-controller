import unittest

from suqc.CommandBuilder.mixins.OppMixin import OppMixin

from suqc.CommandBuilder.interfaces.CommandArguments import CommandArguments


class BaseMixinClass(OppMixin):
    _arguments = CommandArguments()


class TestOppMixin(unittest.TestCase):
    mixin = BaseMixinClass()

    def test_opp_exec(self):
        expected = "any_command"
        self.mixin.opp_exec(expected)
        self.assertEqual(self.mixin._arguments["--opp-exec"], expected)

    def test_opp_argument(self):
        expected_key = "any_key"
        expected_value = "any_value"
        self.mixin.opp_argument(expected_key, expected_value)
        self.assertEqual(self.mixin._arguments[f"--opp.{expected_key}"], expected_value)

    def test_omnet_tag(self):
        expected = "any_tag"
        self.mixin.omnet_tag(expected)
        self.assertEqual(self.mixin._arguments["--omnet-tag"], expected)

