import unittest

from suqc.CommandBuilder.mixins.ControlMixin import ControlMixin

from suqc.CommandBuilder.interfaces.CommandArguments import CommandArguments


class BaseMixinClass(ControlMixin):
    _arguments = CommandArguments()


class testControlMixin(unittest.TestCase):
    mixin = BaseMixinClass()

    def test_control_tag(self):
        expected = "any_tag"
        self.mixin.control_tag(expected)
        self.assertEqual(self.mixin._arguments["--control-tag"], expected)

    def test_with_control(self):
        expected = "any_script"
        self.mixin.with_control(expected)
        self.assertEqual(self.mixin._arguments["--with-control"], expected)

    def test_control_use_local(self):
        expected = None
        self.mixin.control_use_local()
        self.assertEqual(self.mixin._arguments["--control-use-local"], expected)

    def test_control_argument(self):
        expected_key = "any_key"
        expected_value = "any_value"
        self.mixin.control_argument(expected_key, expected_value)
        self.assertEqual(self.mixin._arguments[f"--ctrl.{expected_key}"], expected_value)
