from suqc.CommandBuilder.interfaces.Python3Command import Python3Command
from suqc.CommandBuilder.mixins.BaseMixin import BaseMixin
from suqc.CommandBuilder.mixins.VadereMixin import VadereMixin


class VadereCommand(Python3Command, BaseMixin, VadereMixin):

    def _set_sub_command(self) -> None:
        self._sub_command = "vadere"
