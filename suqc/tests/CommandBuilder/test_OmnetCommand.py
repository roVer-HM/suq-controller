import unittest
from unittest import mock
from unittest.mock import patch

from suqc.CommandBuilder.mixins.OppMixin import OppMixin
from suqc.CommandBuilder.interfaces.Python3Command import Python3Command
from suqc.CommandBuilder.OmnetCommand import OmnetCommand
from suqc.CommandBuilder.mixins.BaseMixin import BaseMixin


class TestOmnetCommand(unittest.TestCase):

    @patch.multiple(OmnetCommand, __abstractmethods__=set())
    @mock.patch('suqc.CommandBuilder.OmnetCommand.OmnetCommand._set_sub_command')
    def test__init__(self, mock_set_sub_command: mock.MagicMock):
        command = OmnetCommand()
        mock_set_sub_command.assert_called_once()
        self.assertTrue(isinstance(command, Python3Command))
        self.assertTrue(isinstance(command, OppMixin))
        self.assertTrue(isinstance(command, BaseMixin))

    def test_set_sub_command(self) -> None:
        expected = "omnet"
        command = OmnetCommand()
        self.assertEqual(command._sub_command, expected)
