from pyDOE import lhs


class LatinHyperCubeSampling:
    def __init__(self, parameters, number_of_samples=10):
        self.parameters = parameters
        self.number_of_samples = number_of_samples

    def get_single_sample(self, values):

        sample = self.__initialize_sample_dict()
        check = len(sample.keys())

        for k in range(len(values)):
            parameter = self.parameters[k]
            parameter.set_val(values[k])

            if check == 0:
                sample.update(parameter.to_dict())
            else:
                simulator = parameter.get_simulator()
                sample[simulator].update(parameter.to_dict())

        return sample

    def get_dictionary(self, number_of_samples=None):

        if number_of_samples is not None:
            self.number_of_samples = number_of_samples

        lhs_mapped = self.__get_sampling_vals()
        par_var = []

        for sample in lhs_mapped:
            pars = self.get_single_sample(sample)
            par_var.append(pars)

        return par_var

    def __get_sampling_vals(self):

        lhs_without_ranges = lhs(len(self.parameters), self.number_of_samples)
        lhs_mapped = lhs_without_ranges.copy()

        for ind in range(0, len(self.parameters)):

            parameter = self.parameters[ind]
            interval = parameter.get_interval()
            lower_bound = parameter.get_lower_bound()

            lhs_mapped[:, ind] = lower_bound + lhs_mapped[:, ind] * interval

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

    def __init__(self, name, unit=None, simulator=None, value=None, range=None):
        self.name = name
        self.value = value
        self.unit = unit
        self.simulator = simulator
        self.set_range(range)

    def set_val(self, val):
        self.value = val

    def set_range(self, range):
        # reorder
        self.range = range

    def get_range(self):
        return self.range

    def get_interval(self):
        interval = self.range[1] - self.range[0]
        return interval

    def get_lower_bound(self):
        return self.range[0]

    def get_upper_bound(self):
        return self.range[1]

    def get_simulator(self):
        return self.simulator

    def to_dict(self):
        if self.unit is None:
            return {self.name: self.value}
        else:
            #return {self.name: (self.value, self.unit)}
            return {self.name: f"{self.value}{self.unit}"}
