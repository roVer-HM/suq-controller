import abc
import os
import subprocess
import time
from abc import ABC
from typing import Tuple, List

from suqc.CommandBuilder.interfaces.Command import Command


class Python3Command(Command, ABC):
    _sub_command: str = None
    _script: str = None

    def __init__(self):
        super().__init__()
        self._set_sub_command()

    @abc.abstractmethod
    def _set_sub_command(self) -> None:
        pass

    def __str__(self):
        return f"{self._executable} {self._script} {self._sub_command} {self._arguments}"

    def _set_executable(self) -> None:
        self._executable = "python3"

    def force_set_run_name(self, run_name: str):
        self._arguments["--run-name"] = run_name
        return self

    def run(self, cwd: str, file_name: str) -> Tuple[int, float]:
        time_started = time.time()
        t: str = time.strftime("%H:%M:%S", time.localtime(time_started))
        print(f"{t}\t Call {str(self)}")

        run_command: List[str] = [self._executable, file_name, self._sub_command] + list(self._arguments)
        return_code: int = subprocess.check_call(
            run_command,
            env=os.environ,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=cwd,
            timeout=15000,  # stop simulation after 15000s
        )
        process_duration = time.time() - time_started
        return return_code, process_duration
