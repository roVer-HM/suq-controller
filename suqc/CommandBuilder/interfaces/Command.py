import abc
import os
import subprocess

from suqc.CommandBuilder.interfaces.CommandArguments import CommandArguments


class Command(abc.ABC):
    _executable: str = None
    _arguments: CommandArguments = None
    _cwd = None

    def __init__(self, cwd: str):
        self._cwd = cwd
        self._set_executable()
        self._arguments = CommandArguments()

    @abc.abstractmethod
    def __str__(self):
        pass

    @abc.abstractmethod
    def _set_executable(self) -> None:
        pass

    @abc.abstractmethod
    def run(self) -> None:
        pass
