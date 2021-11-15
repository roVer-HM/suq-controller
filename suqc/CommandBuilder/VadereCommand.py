from suqc.CommandBuilder.interfaces.CommandArguments import CommandArguments
from suqc.CommandBuilder.interfaces.Python3Command import Python3Command
from suqc.CommandBuilder.mixins.BaseMixin import BaseMixin
from suqc.CommandBuilder.mixins.VadereMixin import VadereMixin


class VadereCommand(Python3Command, BaseMixin, VadereMixin):

    def _set_sub_command(self) -> None:
        self._sub_command = "vadere"

    # def _set_command_defaults(self) -> None:
    #     self._arguments = CommandArguments([("--default_vadere_key", "default_vadere_value")])
