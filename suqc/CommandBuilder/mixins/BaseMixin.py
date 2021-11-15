from abc import ABC
from typing import List


class BaseMixin(ABC):
    def qoi(self, files: List[str]):
        self._arguments["--qoi"] = files
        return self

    def pre(self, commands: List[str]):
        self._arguments["--pre"] = commands
        return self

    def result_dir(self, result_dir: str):
        self._arguments["--resultdir"] = result_dir
        return self

    def write_container_log(self):
        self._arguments["--write-container-log"] = None
        return self

    def experiment_label(self, label: str):
        self._arguments["--experiment-label"] = label
        return self

    def override_host_config(self):
        self._arguments["--override-host-config"] = None
        return self

    def run_name(self, run_name: str):
        self._arguments["--run-name"] = run_name
        return self

    def cleanup_policy(self, policy: str):
        self._arguments["--cleanup-policy"] = policy
        return self

    def reuse_policy(self, policy: str):
        self._arguments["--reuse-policy"] = policy
        return self

    def verbose(self):
        self._arguments["--verbose"] = None
        return self
