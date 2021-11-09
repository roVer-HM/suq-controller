import abc
import os
import subprocess
from suqc.CommandBuilder.interfaces import CommandArguments


class Command(abc.ABC):
    _executable: str = None
    _sub_command: str = None
    _arguments: CommandArguments = None

    def __init__(self):
        self.set_executable()
        self.set_sub_command()
        self.set_command_defaults()

    def __str__(self):
        return f"{self._executable} {self._sub_command} {self._arguments}"

    def __iter__(self):
        return iter(self._arguments)

    @abc.abstractmethod
    def set_executable(self) -> None:
        pass

    @abc.abstractmethod
    def set_sub_command(self) -> None:
        pass

    @abc.abstractmethod
    def set_command_defaults(self) -> None:
        pass

    def run(self):
        print(f"(just print) Running: {str(self)}")

    # todo: Mario : change to run after finished and remove run
    def run_for_real(self):
        terminal_command = ['python3',
                            'run_script.py',
                            'vadere-opp',
                            '--create-vadere-container',
                            '--override-host-config',
                            '--vadere-tag', 'latest',
                            '--omnet-tag', 'latest',
                            '--qoi',
                            'degree_informed_extract.txt',
                            'poisson_parameter.txt',
                            'time_95_informed.txt',
                            '--run-name', 'Sample__0_0',
                            '--experiment-label', 'out']
        return_code = subprocess.check_call(
            terminal_command,
            env=os.environ,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd='/home/mweidner/crownet/analysis/uq/simulation_studies/tutorial_simple_detour/results/simulation_runs/Sample__0_0',
            timeout=15000,  # stop simulation after 15000s
        )
        return return_code
