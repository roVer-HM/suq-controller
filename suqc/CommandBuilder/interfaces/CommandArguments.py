from collections import MutableMapping


class CommandArguments(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def set(self, key, value, override=True):
        if override or ( not override and key not in self.store):
            self.store[key] = value
        

    def __iter__(self):
        argument_list = []
        for i in self.store.items():
            argument_list.append(str(i[0]))
            if type(i[1]) == list:
                for ii in i[1]:
                    argument_list.append(str(ii))
            else:
                if i[1]: # skip bool flags (value == None, f.e. --verbose)
                    argument_list.append(str(i[1]))
        return iter(argument_list)

    def __len__(self):
        return len(self.store)

    def __str__(self):
        def to_string(item):
            return " ".join(item) if type(item) == list else str(item)

        argument_string = " ".join([f"{i[0]} {to_string(i[1])}" for i in self.store.items()])

        return argument_string
