from pyDOE import lhs
import numpy as np
import abc
import copy

class RoverSampling(metaclass=abc.ABCMeta):

    def __init__(self, parameters=None, parameters_dependent = None ):
        self.parameters = parameters
        self.parameters_dependent = parameters_dependent

    @abc.abstractmethod
    def get_sampling_vals(self):
        pass


    def get_sampling(self):

        sample_vals = self.get_sampling_vals()

        par_var = list()

        for sample in sample_vals:
            pars = self.get_single_sample(sample)
            par_var.append(copy.deepcopy(pars))

        return par_var

    def __initialize_sample_dict(self):

        simulators = list()

        for parameter in self.parameters:
            sim = parameter.get_simulator()
            if sim is not None:
                simulators.append(sim)

        for parameter in self.parameters_dependent:
            sim = parameter.get_simulator()
            if sim is not None:
                simulators.append(sim)

        simulators = list(set(simulators))

        if len(simulators) > 0:
            pars = dict()
            for simulator in simulators:
                pars.update({simulator: {}})
        else:
            pars = {}
        return pars

    def get_single_sample(self, values):

        #if isinstance(values,float) or isinstance(values,int):
         #   values = [values]

        sample = self.__initialize_sample_dict()
        check = len(sample.keys())

        k = 0
        for parameter in self.parameters:

            if parameter.list_index is None:
                parameter.set_val(values[k])
                k += 1
            else:
                for index in parameter.list_index:
                    parameter.set_val(values[k],index)
                    k += 1

            if check == 0:
                sample.update(parameter.to_dict())
            else:
                simulator = parameter.get_simulator()
                sample[simulator].update(parameter.to_dict())

        for dep in self.parameters_dependent:

            dep.set_val(self.parameters)

            if check == 0:
                sample.update(dep.to_dict())
            else:
                simulator = dep.get_simulator()
                sample[simulator].update(dep.to_dict())

        return sample



class RoverSamplingLatinHyperCube(RoverSampling):

    def __init__(self,parameters=None, parameters_dependent = None, number_of_samples=10):
        self.number_of_samples = number_of_samples
        super(RoverSamplingLatinHyperCube, self).__init__(parameters=parameters, parameters_dependent=parameters_dependent)


    def get_sampling_vals(self):

        number = 0
        for para in self.parameters:
            number = number + para.get_number_of_parameters()


        lhs_without_ranges = lhs(number, self.number_of_samples)
        lhs_mapped = lhs_without_ranges.copy()

        ind = 0
        for parameter in self.parameters:

            if parameter.get_number_of_parameters() == 1:

                interval = parameter.get_interval()
                lower_bound = parameter.get_lower_bound()

                lhs_mapped[:, ind] = lower_bound + lhs_mapped[:, ind] * interval
                ind += 1
            else:

                for c in range(parameter.get_number_of_parameters()):

                    interval = parameter.get_interval()[c]
                    lower_bound = parameter.get_lower_bound()[c]

                    lhs_mapped[:, ind] = lower_bound + lhs_mapped[:, ind] * interval
                    ind += 1

        return lhs_mapped



class RoverSamplingFullFactorial(RoverSampling):

    def __init__(self, parameters=None, parameters_dependent=None):
        super(RoverSamplingFullFactorial, self).__init__(parameters=parameters, parameters_dependent=parameters_dependent)


    def get_sampling_vals(self):

        par_var, x = list(), list()

        for para in self.parameters:
            x.append( para.get_stages() )

        full_factorial = np.meshgrid(*x, indexing="ij")
        full_factorial = np.concatenate(np.transpose(full_factorial))

        if len(self.parameters) == 1:
            full_factorial = [[val] for val in full_factorial]

        return full_factorial






class Parameter:
    @classmethod
    def from_dict(cls, par_dict):
        pass

    def __init__(self, name, unit=None, simulator=None, value=None, range=None, list = None, list_index = None, stages = None):
        self.name = name
        self.value = value
        self.unit = unit
        self.simulator = simulator
        self.set_range(range)
        self.list_index = list_index
        self.list = list
        self.set_stages(stages)

    def get_stages(self):
        return self.stages

    def set_stages(self, stages):

        if isinstance(stages,int):
            range = self.get_range()
            stages = np.linspace(range[0],range[1], stages)

        self.stages = stages


    def get_val(self):
        return self.value

    def set_val(self, val, index = None):

        if (val - int(val)) == 0:
            val = int(val)

        if index is None:
            self.value = val
        else:
            if self.value is None:
                self.value = self.list
            self.value[index] = val

    def set_range(self, range):
        # reorder
        self.range = range

    def get_range(self):
        return self.range

    def get_interval(self):
        if self.list_index is None:
            interval = self.range[1] - self.range[0]
        else:
            interval = [ item[1] - item[0] for item in self.range ]
        return interval

    def get_lower_bound(self):
        if self.list_index is None:
            return self.range[0]
        else:
            return [ item[0] for item in self.range ]

    def get_upper_bound(self):
        if self.list_index is None:
            return self.range[1]
        else:
            return [item[1] for item in self.range]


    def get_simulator(self):
        return self.simulator

    def to_dict(self):



        if self.unit is None:
            val = self.value
        else:
            val = f"{self.value}{self.unit}"

        return {self.name: val}

    def get_number_of_parameters(self):
        if self.list_index is None:
            return 1
        else:
            return len(self.list_index)




class DependentParameter(Parameter):

    def __init__(self, name, equation=None, unit=None, simulator=None, value=None, range=None, list = None, list_index = None):

        self.equation = equation
        super().__init__(name = name, unit =unit, simulator = simulator, value=value, list = list, list_index=list_index)


    def set_val(self, parameter = None):

        eqn = self.equation

        if parameter is not None:
            for para in parameter:
                val = para.get_val()
                eqn = eqn.replace( para.name, str(val) )

            eqn = eqn.replace("=","")

        eqn = eqn.replace("=", "")
        function_val = eval(eqn)

        if isinstance(function_val, float):
            if (function_val - int(function_val)) == 0:
                function_val = int(function_val)
        # to do for list
        self.value = function_val
