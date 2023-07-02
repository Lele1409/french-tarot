def printAllGameFields(gameInstance):
    for field_name, field_value in vars(gameInstance).items():
        print(field_name.ljust(35), field_value)
        if field_name == 'players':
            for player in field_value:
                for field_name_, field_value_ in vars(player).items():
                    print('└──', field_name_.ljust(35), field_value_)
