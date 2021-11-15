import abc
import os
import subprocess
from abc import ABC

from suqc.CommandBuilder.interfaces.Command import Command


class Python3Command(Command, ABC):
    _sub_command: str = None
    _script: str = None

    def __init__(self, cwd: str, script: str):
        super().__init__(cwd)
        self._set_sub_command()
        self._script = script

    @abc.abstractmethod
    def _set_sub_command(self) -> None:
        pass

    def __str__(self):
        return f"{self._executable} {self._script} {self._sub_command} {self._arguments}"

    def _set_executable(self) -> None:
        self._executable = "python3"

    def run(self):
        print(f"(just print) Running: {str(self)}")
        run_command = [self._executable, self._script, self._sub_command] + list(self._arguments)
        return_code = subprocess.check_call(
            run_command,
            env=os.environ,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=self._cwd,
            timeout=15000,  # stop simulation after 15000s
        )
        return return_code
