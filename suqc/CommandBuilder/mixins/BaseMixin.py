from abc import ABC
from typing import List


class BaseMixin(ABC):
    def qoi(self, files: List[str], override = True):
        self._arguments.set("--qoi", files, override)
        return self

    def pre(self, commands: List[str], override = True):
        self._arguments.set("--pre", commands, override)
        return self

    def result_dir(self, result_dir: str, override = True):
        self._arguments.set("--resultdir", result_dir, override)
        return self

    def write_container_log(self):
        self._arguments["--write-container-log"] = None
        return self

    def experiment_label(self, label: str, override = True):
        self._arguments.set("--experiment-label", label, override)
        return self

    def override_host_config(self, run_name: str, override = True):
        self._arguments.set("--override-host-config", None, override)
        self._arguments.set("--run-name", run_name, override)
        return self

    def cleanup_policy(self, policy: str, override=True):
        self._arguments.set("--cleanup-policy", policy, override)
        return self

    def reuse_policy(self, policy: str, override = True):
        self._arguments.set("--reuse-policy", policy, override)
        return self

    def verbose(self):
        self._arguments["--verbose"] = None
        return self
