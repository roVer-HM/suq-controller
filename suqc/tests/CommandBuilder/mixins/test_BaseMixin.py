import unittest

from suqc.CommandBuilder.interfaces.CommandArguments import CommandArguments

from suqc.CommandBuilder.mixins.BaseMixin import BaseMixin


class BaseMixinClass(BaseMixin):
    _arguments = CommandArguments()


class TestBaseMixin(unittest.TestCase):
    mixin = BaseMixinClass()

    def test_qoi(self):
        expected = ["qoi_1", "qoi_2"]
        self.mixin.qoi(expected)
        self.assertEqual(self.mixin._arguments["--qoi"], expected)

    def test_pre(self):
        expected = ["pre_1", "pre_2"]
        self.mixin.pre(expected)
        self.assertEqual(self.mixin._arguments["--pre"], expected)

    def test_result_dir(self):
        expected = "any_dir"
        self.mixin.result_dir(expected)
        self.assertEqual(self.mixin._arguments["--resultdir"], expected)

    def test_write_container_log(self):
        expected = None
        self.mixin.write_container_log()
        self.assertEqual(self.mixin._arguments["--write-container-log"], expected)

    def test_experiment_label(self):
        expected = "any_label"
        self.mixin.experiment_label(expected)
        self.assertEqual(self.mixin._arguments["--experiment-label"], expected)

    def test_override_host_config(self):
        expected_run_name = "any_run_name"
        expected_override_host_config = None
        self.mixin.override_host_config(expected_run_name)
        self.assertEqual(self.mixin._arguments["--run-name"], expected_run_name)
        self.assertEqual(self.mixin._arguments["--override-host-config"], expected_override_host_config)

    def test_cleanup_policy(self):
        expected = "any_policy"
        self.mixin.cleanup_policy(expected)
        self.assertEqual(self.mixin._arguments["--cleanup-policy"], expected)

    def test_reuse_policy(self):
        expected = "any_policy"
        self.mixin.reuse_policy(expected)
        self.assertEqual(self.mixin._arguments["--reuse-policy"], expected)

    def test_verbose(self):
        expected = None
        self.mixin.verbose()
        self.assertEqual(self.mixin._arguments["--verbose"], expected)
