import subprocess
import unittest
from unittest import mock
from unittest.mock import patch

from suqc.CommandBuilder.interfaces.Python3Command import Python3Command
from suqc.CommandBuilder.interfaces.CommandArguments import CommandArguments


class TestPython3Command(unittest.TestCase):
    @patch.multiple(Python3Command, __abstractmethods__=set())
    @mock.patch('suqc.CommandBuilder.interfaces.Python3Command.Python3Command._set_sub_command')
    def test__init__(self, mock_set_sub_command: mock.MagicMock):
        py3_command = Python3Command()
        self.assertEqual(py3_command._executable, "python3")
        self.assertEqual(py3_command.timeout, 15000)
        mock_set_sub_command.assert_called_once()

    @patch.multiple(Python3Command, __abstractmethods__=set())
    def test__str__(self):
        py3_command = Python3Command()
        py3_command._script = "test.py"
        py3_command._sub_command = "sub-command"
        py3_command._arguments = CommandArguments({"--key": "value"})
        stringed = str(py3_command)
        self.assertEqual(stringed, "python3 test.py sub-command --key value")

    @patch.multiple(Python3Command, __abstractmethods__=set())
    def test_set_script(self):
        py3_command = Python3Command()
        value = "test.py"
        py3_command.set_script(value)
        self.assertEqual(py3_command._script, value)

    @patch.multiple(Python3Command, __abstractmethods__=set())
    def test_force_set_run_name(self):
        py3_command = Python3Command()
        value = "any_name"
        py3_command.force_set_run_name(value)
        self.assertEqual(py3_command._arguments["--run-name"], value)

    @patch.multiple(Python3Command, __abstractmethods__=set())
    @mock.patch('time.time', mock.MagicMock(return_value=42))
    @mock.patch('time.strftime', mock.MagicMock(return_value="42"))
    @mock.patch('os.environ', "any_environment")
    @mock.patch("subprocess.check_call")
    def test_run(self, mock_check_call: mock.MagicMock):
        py3_command = Python3Command()
        cwd = "any_cwd"
        py3_command._sub_command = "sub-command"
        py3_command._arguments = CommandArguments({"--key": "value"})
        ret_code, duration = py3_command.run(cwd=cwd, file_name="any_file.py")
        mock_check_call.assert_called_once_with(['python3', 'any_file.py', 'sub-command', '--key', 'value'],
                                                env="any_environment",
                                                stdout=subprocess.DEVNULL,
                                                stderr=subprocess.DEVNULL,
                                                cwd=cwd,
                                                timeout=py3_command.timeout)
        self.assertEqual(duration, 0)


if __name__ == '__main__':
    unittest.main()
