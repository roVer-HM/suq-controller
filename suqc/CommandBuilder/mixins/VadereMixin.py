from abc import ABC
import os

class VadereMixin(ABC):
    def scenario_file(self, file: str, override = True):
        key = "--scenario-file"
        self._arguments.set(key, file, override)
        return self

    def create_vadere_container(self, override = True):
        self._arguments.set("--create-vadere-container", None, override)
        return self

    def vadere_tag(self, tag: str, override = True):
        self._arguments.set("--vadere-tag", tag, override)
        return self

    def v_wait_timeout(self, timeout_s: int, override = True):
        self._arguments.set("--v.wait-timeout", timeout_s, override)
        return self

    def v_traci_port(self, port: int, override = True):
        self._arguments.set("--v.traci-port", port, override)
        return self

    def v_loglevel(self, level: str, override = True):
        self._arguments.set("--v.loglevel", level, override)
        return self

    def v_logfile(self, file: str, override = True):
        self._arguments.set("--v.logfile", file, override)
        return self

    # todo not implemented in roveranalyzer 
    # def vadere_argument(self, key: str, value: str, override: bool = True):
    #     self._arguments.set(f"--vadere.{key}", value, override)
    #     return self

    def get_scenario_file(self):
        return self._arguments.get("--scenario-file")

    def is_scenario_file_set(self):
        return self.get_scenario_file() != None
