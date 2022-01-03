from abc import ABC


class SumoMixin(ABC):

    def create_sumo_container(self, override: True):
        self._arguments.set("--crate-sumo-container", None, override)
        return self

    def sumo_tag(self, tag: str, override: True):
        self._arguments.set("--sumo-tag", tag, override)
        return self

    def sumo_argument(self, key: str, value: str, override: True):
        self._arguments.set(f"--sumo{key}", value, override)
        return self
