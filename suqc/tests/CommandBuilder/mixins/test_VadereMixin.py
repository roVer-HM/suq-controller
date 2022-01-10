import unittest

from suqc.CommandBuilder.mixins.VadereMixin import VadereMixin

from suqc.CommandBuilder.interfaces.CommandArguments import CommandArguments


class BaseMixinClass(VadereMixin):
    _arguments = CommandArguments()


class TestVadereMixin(unittest.TestCase):
    mixin = BaseMixinClass()

    def test_scenario_file(self):
        expected = "any_file"
        self.mixin.scenario_file(expected)
        self.assertEqual(self.mixin._arguments["--scenario-file"], expected)

    def test_create_vadere_container(self):
        expected = None
        self.mixin.create_vadere_container()
        self.assertEqual(self.mixin._arguments["--create-vadere-container"], expected)

    def test_vadere_tag(self):
        expected = "any_tag"
        self.mixin.vadere_tag(expected)
        self.assertEqual(self.mixin._arguments["--vadere-tag"], expected)

    def test_v_wait_timeout(self):
        expected = 42
        self.mixin.v_wait_timeout(expected)
        self.assertEqual(self.mixin._arguments["--v.wait-timeout"], expected)

    def test_v_traci_port(self):
        expected = 42
        self.mixin.v_traci_port(expected)
        self.assertEqual(self.mixin._arguments["--v.traci-port"], expected)

    def test_v_loglevel(self):
        expected = "any_level"
        self.mixin.v_loglevel(expected)
        self.assertEqual(self.mixin._arguments["--v.loglevel"], expected)

    def test_v_logfile(self):
        expected = "any_file"
        self.mixin.v_logfile(expected)
        self.assertEqual(self.mixin._arguments["--v.logfile"], expected)
