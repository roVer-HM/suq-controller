import unittest
from unittest import mock

from suqc.CommandBuilder.JarCommand import JarCommand


class TestJarCommand(unittest.TestCase):

    # @patch.multiple(Python3Command, __abstractmethods__=set())
    # @mock.patch('suqc.CommandBuilder.interfaces.Python3Command.Python3Command._set_sub_command')
    # def test__init__(self, mock_set_sub_command: mock.MagicMock):
    #     py3_command = Python3Command()
    #     self.assertEqual(py3_command._executable, "python3")
    #     self.assertEqual(py3_command.timeout, 15000)
    #     mock_set_sub_command.assert_called_once()

    @mock.patch('suqc.CommandBuilder.JarCommand._set_sub_command')
    def test__init__(self, mock_set_sub_command: mock.MagicMock):
        file_name = "any_file"
        jar_command = JarCommand(jar_file=file_name)
        self.assertEqual(jar_command._sub_command, "")

    def test_set_sub_command(self) -> None:
        self._sub_command = f"-jar {self.__jar_file}"
