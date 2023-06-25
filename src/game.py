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
            matchPoints = [0 * playerCount]
        self.matchPoints = matchPoints

        # deck: can be set from previous game, or a new deck will be created and shuffled
        if deck is None:
            deck = self.create_deck()
            shuffle(deck)
        self.deck = deck

        # init variables
        self.playedTricks = []
        self.dog = []
        self.players = [Player() for player in range(playerCount)]

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
        dogSize = 6
        cardsInTheDog = 0

        while self.deck:
            for player in self.players:
                # Cards can only be added to the dog one at a time, it cannot be the last card of the deal, and a
                # player needs to be getting cards in between. This means that at the end, if the dog isn't full, every
                # possible card will need to go into the dog still keeping the distancing of three cards given to
                # players, this state starts when there are fewer cards left than (dogSize-cardsInTheDog+1)*3
                if len(self.deck) < (dogSize + 1) * 3:
                    self.dog.append(self.deck[0])

                cardsDealt = [self.deck.pop(i) for i in range(3)]
                player.addCardsToHand(cardsDealt)


class Player:
    def __init__(self):
        self.cards = []

    def addCardsToHand(self, card: str | list) -> None:
        self.cards.append(card)


class GameException(Exception):
    """Class for errors"""


if __name__ == '__main__':
    game = Game(3)
    print(game.deck)
