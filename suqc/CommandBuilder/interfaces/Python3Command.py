from abc import ABC

from suqc.CommandBuilder.interfaces.Command import Command


class Python3Command(Command, ABC):
    def set_executable(self) -> None:
        self._executable = "python3"
