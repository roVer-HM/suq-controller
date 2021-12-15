from suqc.CommandBuilder.interfaces.JavaCommand import JavaCommand


class JarCommand(JavaCommand):
    def __init__(self, jar_file: str):
        self.__jar_file: str = jar_file
        super().__init__()

    def _set_sub_command(self) -> None:
        self._sub_command = f"-jar {self.__jar_file}"
