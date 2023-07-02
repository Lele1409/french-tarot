def printAllGameFields(gameInstance):
    for field_name, field_value in vars(gameInstance).items():
        print(field_name.ljust(35), field_value)
        if field_name == 'players':
            for player in field_value:
                for field_name_, field_value_ in vars(player).items():
                    print('└──', field_name_.ljust(35), field_value_)


class Memoize:
    def __init__(self, f):
        self.f = f
        self.memo = {}

    def __call__(self, *args):
        if args not in self.memo:
            self.memo[args] = self.f(*args)
        # Warning: You may wish to do a deepcopy here if returning objects
        return self.memo[args]
