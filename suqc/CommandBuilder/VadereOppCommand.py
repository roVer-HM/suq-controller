from suqc.CommandBuilder.interfaces.Python3Command import Python3Command
from suqc.CommandBuilder.mixins.BaseMixin import BaseMixin
from suqc.CommandBuilder.mixins.VadereMixin import VadereMixin
from suqc.CommandBuilder.mixins.OppMixin import OppMixin


class VadereOppCommand(Python3Command, BaseMixin, VadereMixin, OppMixin):

    def _set_sub_command(self) -> None:
        self._sub_command = "vadere-opp"

    def set_directory(self, dir: str):
        self._cwd = dir

    # def _set_command_defaults(self) -> None:
    #     self._arguments = CommandArguments([("--default_vadere_opp_key", "default_vadere_opp_value")])
