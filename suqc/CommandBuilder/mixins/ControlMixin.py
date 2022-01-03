from abc import ABC


class ControlMixin(ABC):
    def control_tag(self, tag: str, override = True):
        self._arguments.set("--control-tag", tag, override)
        return self

    def with_control(self, control_script: str, override = True):
        self._arguments.set("--with-control", control_script, override)
        return self

    def control_use_local(self, override = True):
        self._arguments.set("--control-use-local", None, override)
        return self

    def control_argument(self, key: str, value: str, override = True):
        self._arguments.set(f"--ctrl.{key}", value, override)
        return self
