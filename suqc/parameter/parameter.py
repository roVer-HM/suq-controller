from pyDOE import lhs

import copy, numpy

class LatinHyperCubeSampling:
    def __init__(self, parameters=None, parameters_dependent = None, number_of_samples=10, ):
        self.parameters = parameters
        self.parameters_dependent = parameters_dependent
        self.number_of_samples = number_of_samples

    def get_single_sample(self, values):

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





    def get_sampling(self, number_of_samples=None):

        if number_of_samples is not None:
            self.number_of_samples = number_of_samples

        # if len(self.parameters) == 1:
        #     lhs_mapped = numpy.linspace( self.parameters[0].get_lower_bound(),  self.parameters[0].get_upper_bound(), self.number_of_samples)
        #     lhs_mapped = [[val] for val in lhs_mapped.tolist()]
        # else:
        #     lhs_mapped = self.__get_sampling_vals()

        lhs_mapped = self.__get_sampling_vals()

        par_var = list()

        for sample in lhs_mapped:
            pars = self.get_single_sample(sample)
            par_var.append(copy.deepcopy(pars))

        return par_var




    def __get_sampling_vals(self):

        number = 0
        for para in self.parameters:
            number = number + para.get_number_of_parameters()

        lhs_without_ranges = lhs(number, self.number_of_samples)
        lhs_mapped = lhs_without_ranges.copy()

        ind = 0
        for parameter in self.parameters:

            if parameter.get_number_of_parameters() is 1:

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

    def __initialize_sample_dict(self):

        simulators = list()

        for parameter in self.parameters:
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





class Parameter:
    @classmethod
    def from_dict(cls, par_dict):
        pass

    def __init__(self, name, unit=None, simulator=None, value=None, range=None, list = None, list_index = None):
        self.name = name
        self.value = value
        self.unit = unit
        self.simulator = simulator
        self.set_range(range)
        self.list_index = list_index
        self.list = list

    def get_val(self):
        return self.value

    def set_val(self, val, index = None):
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
        return self.range[1]

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


    def set_val(self, parameter):

        eqn = self.equation

        for para in parameter:
            val = para.get_val()
            eqn = eqn.replace( para.name, str(val) )

        eqn = eqn.replace("=","")
        function_val = eval(eqn)

        self.value = function_val


