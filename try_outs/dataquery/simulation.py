#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

from try_outs.environment import EnvironmentManager

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


class SimulationRun(object):

    def __init__(self, sc: EnvironmentManager):
        self._scm = sc

    def simulate(self):
        model = self._scm.get_config(key="model")

        if model == "vadere":  # TODO: this should be handeled in an Enum
            pass
        else:
            raise Exception(f"No model {model} is available.")



class RunVadere(object):

    def run(self, scenario):

        # TODO: replace with subprocess

        systemCommand = "java -jar vadere-console.jar " + scenario_file_path + " " + output_path + " -suq"
        status = os.system(systemCommand)

        if status != 0:
            print("Error: VadereConsole exited with return code: %d" % status)
            exit(1)

        return status

