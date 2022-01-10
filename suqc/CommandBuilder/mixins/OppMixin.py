from abc import ABC


class OppMixin(ABC):
    def opp_exec(self, exec: str, override=True):
        self._arguments.set("--opp-exec", exec, override)
        return self

    def opp_argument(self, key: str, value: str, override=True):
        self._arguments.set(f"--opp.{key}", value, override)
        return self

    def omnet_tag(self, tag: str, override=True):
        self._arguments.set("--omnet-tag", tag, override)
        return self
