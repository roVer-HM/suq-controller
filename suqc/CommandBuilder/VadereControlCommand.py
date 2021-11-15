from suqc.CommandBuilder.interfaces.CommandArguments import CommandArguments
from suqc.CommandBuilder.interfaces.Python3Command import Python3Command
from suqc.CommandBuilder.mixins.BaseMixin import BaseMixin
from suqc.CommandBuilder.mixins.VadereMixin import VadereMixin
from suqc.CommandBuilder.mixins.ControlMixin import ControlMixin


class VadereControlCommand(Python3Command, BaseMixin, VadereMixin, ControlMixin):

    def _set_sub_command(self) -> None:
        self._sub_command = "vadere-control"

    # def _set_command_defaults(self) -> None:
    #     self._arguments = CommandArguments([("--default_vadere_control_key", "default_vadere_control_value")])
