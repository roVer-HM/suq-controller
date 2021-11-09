from abc import ABC


class OppMixin(ABC):
    def opp_exec(self, exec: str):
        self._arguments["--opp-exec"] = exec
        return self

    def opp_argument(self, key: str, value: str):
        self._arguments[f"--opp.{key}"] = value
        return self

    def omnet_tag(self, tag: str):
        self._arguments["--omnet-tag"] = tag
        return self
