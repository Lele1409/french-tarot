inputs = ["action_1", "action_2", "action_3", "action_4", "action_5",
          "action_6", "action_7", "action_8", "action_9", "action_10"]


def receive(input):
    if input == "action_1":
        create_game()
        add_player()


class Game():
    room_code = None

    def __init__(self):
        pass


def create_game():
    print("Creating game...")
    game = Game()
    print("Game created.")
    return game.room_code


if __name__ == '__main__':
    for input in inputs:
        receive(input)
