from abc import ABC


class ControlMixin(ABC):
    def control_tag(self, tag: str):
        self._arguments["--control-tag"] = tag
        return self

    def with_control(self, control_script: str):
        self._arguments["--with-control"] = control_script
        return self

    def control_use_local(self):
        self._arguments["--control-use-local"] = None
        return self

    def control_argument(self, key: str, value: str):
        self._arguments[f"--ctrl.{key}"] = value
        return self
