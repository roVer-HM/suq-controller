from suqc.CommandBuilder.interfaces.Python3Command import Python3Command
from suqc.CommandBuilder.mixins.BaseMixin import BaseMixin
from suqc.CommandBuilder.mixins.OppMixin import OppMixin
from suqc.CommandBuilder.mixins.SumoMixin import SumoMixin


class SumoCommand(Python3Command, BaseMixin, SumoMixin, OppMixin):

    def _set_sub_command(self) -> None:
        self._sub_command = "sumo"
