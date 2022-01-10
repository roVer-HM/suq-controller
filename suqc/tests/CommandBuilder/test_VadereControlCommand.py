import unittest
from unittest import mock
from unittest.mock import patch

from suqc.CommandBuilder.mixins.BaseMixin import BaseMixin
from suqc.CommandBuilder.mixins.ControlMixin import ControlMixin
from suqc.CommandBuilder.mixins.VadereMixin import VadereMixin
from suqc.CommandBuilder.interfaces.Python3Command import Python3Command
from suqc.CommandBuilder.VadereControlCommand import VadereControlCommand


class TestVadereControlCommand(unittest.TestCase):

    @patch.multiple(VadereControlCommand, __abstractmethods__=set())
    @mock.patch('suqc.CommandBuilder.VadereControlCommand.VadereControlCommand._set_sub_command')
    def test__init__(self, mock_set_sub_command: mock.MagicMock):
        command = VadereControlCommand()
        mock_set_sub_command.assert_called_once()
        self.assertTrue(isinstance(command, Python3Command))
        self.assertTrue(isinstance(command, VadereMixin))
        self.assertTrue(isinstance(command, ControlMixin))
        self.assertTrue(isinstance(command, BaseMixin))

    def test_set_sub_command(self) -> None:
        expected = "vadere-control"
        command = VadereControlCommand()
        self.assertEqual(command._sub_command, expected)
