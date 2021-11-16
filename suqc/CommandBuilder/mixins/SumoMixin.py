from abc import ABC


class SumoMixin(ABC):

    def create_sumo_container(self):
        self._arguments["--create-sumo-container"] = None
        return self

    def sumo_tag(self, tag: str):
        self._arguments["--sumo-tag"] = tag
        return self

    def sumo_argument(self, key: str, value: str):
        self._arguments[f"--sumo.{key}"] = value
        return self
