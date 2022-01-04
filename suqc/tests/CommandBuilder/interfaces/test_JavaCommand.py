import subprocess
import unittest
from unittest import mock
import copy
from unittest.mock import patch

from suqc.CommandBuilder.interfaces.CommandArguments import CommandArguments
from suqc.CommandBuilder.interfaces.JavaCommand import JavaCommand


class TestJavaCommand(unittest.TestCase):

    @patch.multiple(JavaCommand, __abstractmethods__=set())
    @mock.patch('suqc.CommandBuilder.interfaces.JavaCommand.JavaCommand._set_sub_command')
    def test__init__(self, mock_set_sub_command: mock.MagicMock):
        command = JavaCommand()
        self.assertEqual(command._executable, "java")
        log_levels = [
            "OFF", "FATAL", "TOPOGRAPHY_ERROR",
            "TOPOGRAPHY_WARN", "INFO", "DEBUG", "ALL"]
        self.assertEqual(command.ALLOWED_LOGLVL, log_levels)
        mock_set_sub_command.assert_called_once()

    @patch.multiple(JavaCommand, __abstractmethods__=set())
    def test__str__(self):
        command = JavaCommand()
        command._options = ["option_1", "option_2"]
        command._sub_command = "jar"
        command._main_class = "main"
        command._arguments = CommandArguments({"--key": "value"})
        stringed = str(command)
        self.assertEqual(stringed, "java option_1 option_2 jar main --key value")

        command = JavaCommand()
        stringed = str(command)
        self.assertEqual(stringed, "java")

    @patch.multiple(JavaCommand, __abstractmethods__=set())
    def test__iter__(self):
        command = JavaCommand()
        command._options = ["option_1", "option_2"]
        command._sub_command = "jar"
        command._main_class = "main"
        command._arguments = CommandArguments({"--key": "value"})
        listed = list(command)
        expected = ['java', 'option_1', 'option_2', 'jar', 'main', '--key', 'value']
        self.assertEqual(listed, expected)

    @patch.multiple(JavaCommand, __abstractmethods__=set())
    def test_add_option(self):
        command = JavaCommand()
        option = "any_option"
        command.add_option(option)
        self.assertTrue(option in command._options)

    @patch.multiple(JavaCommand, __abstractmethods__=set())
    def test_main_class(self):
        command = JavaCommand()
        main_class = "main_class"
        command.main_class(main_class)
        self.assertEqual(main_class, command._main_class)

    @patch.multiple(JavaCommand, __abstractmethods__=set())
    def test_add_argument(self):
        command = JavaCommand()
        command.add_argument("key", "value")
        self.assertTrue("key" in command._arguments)
        self.assertEqual(command._arguments["key"], "value")

    @patch.multiple(JavaCommand, __abstractmethods__=set())
    def test_log_level(self):
        command = JavaCommand()
        for level in command.ALLOWED_LOGLVL:
            _command = copy.deepcopy(command)
            _command.log_level(level)
            self.assertTrue("--loglevel" in _command._arguments)
            self.assertEqual(_command._arguments["--loglevel"], level)
        with self.assertRaises(ValueError) as context:
            command.log_level("NOT_ALLOWED")
        expected = f"set loglvl=NOT_ALLOWED not contained in allowed: {command.ALLOWED_LOGLVL}"
        self.assertEqual(str(context.exception), expected)

    @patch.multiple(JavaCommand, __abstractmethods__=set())
    @mock.patch('time.time', mock.MagicMock(return_value=42))
    @mock.patch("subprocess.check_output")
    def test_run(self, mock_check_output: mock.MagicMock):
        command = JavaCommand()
        command._options = ["option_1", "option_2"]
        command._sub_command = "jar"
        command._main_class = "main"
        command._arguments = CommandArguments({"--key": "value"})
        timeout = 1337
        return_code, duration, output_subprocess = command.run(timeout_sec=timeout)
        mock_check_output.assert_called_once_with(['java', 'option_1', 'option_2', 'jar', 'main', '--key', 'value'],
                                                  timeout=timeout,
                                                  stderr=-1)
        self.assertEqual(return_code, 0)
        self.assertEqual(duration, 0)
        self.assertEqual(output_subprocess, None)
        mock_check_output.reset_mock()

        mock_check_output.side_effect = subprocess.TimeoutExpired(cmd="",
                                                                  timeout=timeout,
                                                                  output="stdout",
                                                                  stderr=None)
        ret_code, duration, output_subprocess = command.run(timeout)
        self.assertEqual(ret_code, 1)
        self.assertEqual(duration, timeout)
        self.assertEqual(output_subprocess, {'stdout': 'stdout', 'stderr': None})
        mock_check_output.reset_mock()

        mock_check_output.side_effect = subprocess.CalledProcessError(cmd="",
                                                                      returncode=42,
                                                                      output="stdout",
                                                                      stderr="stderr")
        ret_code, duration, output_subprocess = command.run(timeout)
        self.assertEqual(ret_code, 42)
        self.assertEqual(duration, 0)
        self.assertEqual(output_subprocess, {'stdout': 'stdout', 'stderr': "stderr"})


if __name__ == '__main__':
    unittest.main()
