import unittest
from unittest import mock
import copy
from unittest.mock import patch

from suqc.CommandBuilder.interfaces.Command import Command

from suqc.CommandBuilder.interfaces.CommandArguments import CommandArguments

from suqc.utils.SeedManager.OmnetSeedManager import OmnetSeedManager


class TestCommand(unittest.TestCase):

    @patch.multiple(Command, __abstractmethods__=set())
    @mock.patch('suqc.CommandBuilder.interfaces.Command.Command._set_executable')
    def test__init__(self, mock_set_executable: mock.MagicMock):
        command = Command()
        self.assertEqual(type(command._arguments), CommandArguments)
        mock_set_executable.assert_called_once()


if __name__ == '__main__':
    unittest.main()
