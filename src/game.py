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
        self.dog = []
        self.players = [Player() for _ in range(playerCount)]

    @staticmethod
    def create_deck() -> list:
        """Return a list of the 78 cards: four suits, all trumps and the excuse"""
        suits = ['♤', '♡', '♧', '♢']
        values = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'C', 'Q', 'K']

        trumps = [f"{n}T" for n in range(1, 21 + 1)]
        cards = [f"{values[value]}{suits[suit]}" for suit in range(4) for value in range(14)]

        deck = cards + trumps + ['EX']
        return deck

    def start(self):
        # deal cards
        self.deal()

        # contract
        # play tricks (trick=int)

    def deal(self):
        dogSize = int(self.dogSizes[self.playerCount])
        deals = [False for _ in range(int((78 - dogSize) / 3 + dogSize))]
        for _ in range(dogSize):
            # Don't replace a True with a True, don't have a True beside another True, don't have a leading or an
            # ending True
            i = 0
            while deals[i] or deals[i+1] or deals[i-1] or i == 0:
                i = randint(1, len(deals) - 2)
            deals[i] = True

        nextPlayer = 0
        for deal in deals:
            if deal:
                self.dog.append(self.deck.pop(0))
            else:
                cardsDealt = [self.deck.pop(0) for _ in range(3)]
                self.players[nextPlayer].addCardsToHand(cardsDealt)

                nextPlayer += 1
                if nextPlayer > self.playerCount-1:
                    nextPlayer = 0


class Player:
    def __init__(self):
        self.hand = []

    def addCardsToHand(self, cards: list) -> None:
        for card in cards:
            self.hand.append(card)


class GameException(Exception):
    """Class for errors"""


if __name__ == '__main__':
    game = Game(4)
    game.start()
