import unittest
from unittest import mock
from unittest.mock import patch

from suqc.CommandBuilder.mixins.BaseMixin import BaseMixin
from suqc.CommandBuilder.mixins.VadereMixin import VadereMixin
from suqc.CommandBuilder.interfaces.Python3Command import Python3Command
from suqc.CommandBuilder.VadereCommand import VadereCommand


class TestVadereCommand(unittest.TestCase):


    @patch.multiple(VadereCommand, __abstractmethods__=set())
    @mock.patch('suqc.CommandBuilder.VadereCommand.VadereCommand._set_sub_command')
    def test__init__(self, mock_set_sub_command: mock.MagicMock):
        command = VadereCommand()
        mock_set_sub_command.assert_called_once()
        self.assertTrue(isinstance(command, Python3Command))
        self.assertTrue(isinstance(command, VadereMixin))
        self.assertTrue(isinstance(command, BaseMixin))

    def test_set_sub_command(self) -> None:
        expected = "vadere"
        command = VadereCommand()
        self.assertEqual(command._sub_command, expected)
