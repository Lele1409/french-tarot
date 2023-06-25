from random import shuffle, randint


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
            matchPoints = [0 * playerCount]
        self.matchPoints = matchPoints

        # deck: can be set from previous game, or a new deck will be created and shuffled
        if deck is None:
            deck = self.create_deck()
            shuffle(deck)
        self.deck = deck

        # init variables
        self.dogSizes = {
            3: "6",
            4: "6",
            5: "3"
        }
        self.playedTricks = []
        self.dog = []
        self.players = [Player() for _ in range(playerCount)]

    @staticmethod
    def create_deck() -> list:
        """Return a list of the 78 cards: four suits, all trumps and the excuse"""
        suits = ['♤', '♡', '♧', '♢']
        values = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'C', 'Q', 'K']

        trumps = [f"{n}T" for n in range(1, 21 + 1)]
        cards = [f"{values[value]}{suits[suit]}" for suit in range(4) for value in range(13)]

        deck = cards + trumps + ['EX']
        return deck

    def start(self):
        # deal cards
        self.deal()

        # contract
        # play tricks (trick=int)

    def deal(self):
        dogSize = self.dogSizes[self.playerCount]
        cardsInDog = [(78 - dogSize) / 3 + dogSize * False]
        for _ in range(dogSize):
            i = randint(0, len(cardsInDog) - 1)
            if cardsInDog[i] == True:  # NOQA
                cardsInDog[i+1] = True
            else:
                cardsInDog[i+1] = True

        nextPlayer = 0
        for cardInDog in cardsInDog:
            if cardInDog:
                self.dog.append(self.deck.pop(0))
            else:
                cardsDealt = [self.deck.pop(i) for i in range(3)]
                self.players[nextPlayer].addCardsToHand(cardsDealt)

                nextPlayer += 1
                if nextPlayer > self.playerCount:
                    nextPlayer = 0


class Player:
    def __init__(self):
        self.hand = []

    def addCardsToHand(self, card: list) -> None:
        self.hand.append(card)


class GameException(Exception):
    """Class for errors"""


if __name__ == '__main__':
    game = Game(3)
    print(game.deck)
