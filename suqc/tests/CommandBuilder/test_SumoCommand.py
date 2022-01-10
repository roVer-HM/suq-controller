import unittest
from unittest import mock
from unittest.mock import patch

from suqc.CommandBuilder.mixins.SumoMixin import SumoMixin
from suqc.CommandBuilder.mixins.BaseMixin import BaseMixin
from suqc.CommandBuilder.interfaces.Python3Command import Python3Command
from suqc.CommandBuilder.SumoCommand import SumoCommand


class TestSumoCommand(unittest.TestCase):

    @patch.multiple(SumoCommand, __abstractmethods__=set())
    @mock.patch('suqc.CommandBuilder.SumoCommand.SumoCommand._set_sub_command')
    def test__init__(self, mock_set_sub_command: mock.MagicMock):
        command = SumoCommand()
        mock_set_sub_command.assert_called_once()
        self.assertTrue(isinstance(command, Python3Command))
        self.assertTrue(isinstance(command, SumoMixin))
        self.assertTrue(isinstance(command, BaseMixin))

    def test_set_sub_command(self) -> None:
        expected = "sumo"
        command = SumoCommand()
        self.assertEqual(command._sub_command, expected)
