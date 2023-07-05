import hashlib
import pickle


class Memoize:
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        key = self._get_cache_key(*args)
        if key in self.cache:
            return self.cache[key]
        result = self.func(*args)
        self.cache[key] = result
        return result

    def _get_cache_key(self, *args):
        # Use pickle and hash to create a unique key
        key = pickle.dumps(args)
        return hashlib.sha256(key).hexdigest()


def printAllGameFields(gameInstance):
    for field_name, field_value in vars(gameInstance).items():
        print(field_name.ljust(35), field_value)
        if field_name == 'players':
            for player in field_value:
                for field_name_, field_value_ in vars(player).items():
                    print('└──', field_name_.ljust(35), field_value_)
