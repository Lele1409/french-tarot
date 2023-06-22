from random import shuffle


class Game:
    def __init__(self, playerCount: int, deck=None, matchPoints=None):
        """Validating parameters and initalizing variables"""
        # playerCount: is limited to specific values
        if playerCount not in [3, 4, 5]:
            raise GameException(f"playerCount has to be 3, 4 or 5")
        else:
            self.playerCount = playerCount

        # points: set scores if this is the first game in a match
        if matchPoints is None:
            setPoints = [0 * playerCount]
        self.matchPoints = matchPoints

        # deck: can be set from previous game, or a new deck will be created
        if deck is None:
            self.deck = self.create_deck()
            shuffle(self.deck)
        else:
            self.deck = deck

        # init variables
        self.playedTricks = []

    @staticmethod
    def create_deck() -> list:
        suits = ['♤', '♡', '♧', '♢']
        values = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'C', 'Q', 'K']

        trumps = [f"{n}T" for n in range(1, 21 + 1)]
        cards = [f"{values[j]}{suits[i]}" for i in range(4) for j in range(13)]

        deck = cards + trumps + ['EX']
        return deck


class Player:
    def __init__(self):
        pass


class GameException(Exception):
    """Class for errors"""


if __name__ == '__main__':
    game = Game(3)
    print(game.deck)
