from suqc.CommandBuilder.SumoCommand import SumoCommand
from suqc.CommandBuilder.VadereCommand import VadereCommand
from suqc.CommandBuilder.VadereControlCommand import VadereControlCommand
from suqc.CommandBuilder.VadereOppCommand import VadereOppCommand
from suqc.CommandBuilder.VadereOppControlCommand import VadereOppControlCommand

if __name__ == "__main__":
    # return_value = VadereOppCommand().run_for_real()
    c1 = SumoCommand("a")
    c2 = VadereCommand("b")
    c3 = VadereControlCommand("c")
    c4 = VadereOppCommand("d")
    c5 = VadereOppControlCommand("e")
    listed_arguments = list(c1)
    print(c1)
    print(c2)
    print(c3)
    print(c4)
    print(c5)
    print(listed_arguments)
    print("")

    # examples
    # VadereOppControlCommand().add_vadere_parameter().add_opp_parameter().add_control_parameter().run()
    # SumoCommand().add_sumo_parameter().run()
    # SumoCommand().run()
    pass
