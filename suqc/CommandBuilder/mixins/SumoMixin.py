from abc import ABC


class SumoMixin(ABC):

    def create_sumo_container(self, override: bool = True):
        self._arguments.set("--create-sumo-container", None, override)
        return self

    def sumo_tag(self, tag: str, override: bool = True):
        self._arguments.set("--sumo-tag", tag, override)
        return self

    def sumo_argument(self, key: str, value: str, override: bool = True):
        self._arguments.set(f"--sumo.{key}", value, override)
        return self
