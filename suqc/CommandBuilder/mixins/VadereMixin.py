from abc import ABC


class VadereMixin(ABC):
    def scenario_file(self, file: str):
        self._arguments["--scenario-file"] = file
        return self

    def create_vadere_container(self,):
        self._arguments["--create-vadere-container"] = None
        return self

    def vadere_tag(self, tag: str):
        self._arguments["--vadere-tag"] = tag
        return self

    def v_wait_timeout(self, timeout_s: int):
        self._arguments["--v.wait-timeout"] = timeout_s
        return self

    def v_traci_port(self, port: int):
        self._arguments["--v.traci-port"] = port
        return self

    def v_loglevel(self, level: str):
        self._arguments["--v.loglevel"] = level
        return self

    def v_logfile(self, file: str):
        self._arguments["--v.logfile"] = file
        return self
