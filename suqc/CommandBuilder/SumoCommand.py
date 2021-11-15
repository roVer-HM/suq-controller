from suqc.CommandBuilder.interfaces.CommandArguments import CommandArguments
from suqc.CommandBuilder.interfaces.Python3Command import Python3Command
from suqc.CommandBuilder.mixins.BaseMixin import BaseMixin
from suqc.CommandBuilder.mixins.SumoMixin import SumoMixin


class SumoCommand(Python3Command, BaseMixin, SumoMixin):

    def _set_sub_command(self) -> None:
        self._sub_command = "sumo"

    # def _set_command_defaults(self) -> None:
    #     self._arguments = CommandArguments([("--default_sumo_key", ["default_sumo_value_1", "default_sumo_value_2"])])
