from abc import ABC


class VadereMixin(ABC):
    def scenario_file(self, file: str, override = True):
        self._arguments.set("--scenario-file", file, override)
        return self

    def create_vadere_container(self, override = True):
        self._arguments.set("--create-vadere-container", None, override)
        return self

    def vadere_tag(self, tag: str, override = True):
        self._arguments.set("vadere-tag", tag, override)
        return self

    def v_wait_timeout(self, timeout_s: int, override = True):
        self._arguments.set("v.wait-timeout", timeout_s, override)
        return self

    def v_traci_port(self, port: int, override = True):
        self._arguments.set("v.traci-port", port, override)
        return self

    def v_loglevel(self, level: str, override = True):
        self._arguments.set("v.loglevel", level, override)
        return self

    def v_logfile(self, file: str, override = True):
        self._arguments.set("v.logfile", file, override)
        return self
