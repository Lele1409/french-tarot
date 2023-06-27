from random import shuffle, randint


class Game:
    def __init__(self, playerCount: int, deck=None, matchPoints=None, lastDealer=1):
        # VALIDATE PARAMETERS
        # playerCount: is limited to specific values
        if playerCount not in [3, 4, 5]:
            raise GameException(f"Parameter playerCount has to be 3, 4 or 5")
        else:
            self.playerCount = playerCount

        # points: set scores if this is the first game in a match
        if matchPoints is None:
            matchPoints = [0 * playerCount]
        self.matchPoints = matchPoints

        # deck: can be set from previous game, or a new deck will be created and shuffled
        if deck is None:
            deck = self._create_deck()
            shuffle(deck)
        self.deck = deck

        # lastDealer: can be set from previous game, making the dealer change by one player
        newDealer = lastDealer - 1
        if newDealer < 0:
            self.dealer = self.playerCount - 1
        else:
            self.dealer = newDealer

        # INITIALIZE VARIABLES
        self.dogSizes = {
            3: 6,
            4: 6,
            5: 3
        }
        self.dog = []

        # Create a list of player objects
        self.players = [Player(n) for n in range(playerCount)]

    @staticmethod
    def _create_deck() -> list:
        """Return a list of the 78 cards: four suits, all trumps and the excuse"""
        suits = ['♤', '♡', '♧', '♢']
        values = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'C', 'Q', 'K']

        # Trumps, ex: "15T"
        trumps = [f"{n}T" for n in range(1, 21 + 1)]
        # Suit cards, ex: "1♤" or "K♧"
        cards = [f"{values[value]}{suits[suit]}" for suit in range(len(suits)) for value in range(len(values))]

        # Merge, add excuse "EX"
        deck = cards + trumps + ['EX']
        return deck

    def start(self):
        # deal cards
        self._deal()

        # contract
        self.awaitContracts()

        # play tricks (param trick:int)

    def _deal(self):  # TODO: add start deal at right of dealer
        """Get a list of booleans. For every boolean value, if True a card is put into the dog, if False three cards
        are given to next player starting at the player next to the dealer"""

        # List of booleans specifying the deal type
        deals = self._specifyDealOrder()

        nextPlayer = 0
        for deal in deals:
            if deal == True:  # NOQA | if the card is for the dog
                # Add the first card of the deck to the dog
                self.dog.append(self.deck.pop(0))
            else:
                print(self.deck)
                # Give the three first of the deck cards to the next player
                cardsDealt = [self.deck.pop(0) for _ in range(3)]
                self.players[nextPlayer].addCardsToHand(cardsDealt)

                # Set the nextPlayer to what would be the player to the right of the current player
                nextPlayer -= 1
                if nextPlayer < 0:
                    nextPlayer = self.playerCount - 1

    def _specifyDealOrder(self) -> list:
        """Depending on the playerCount (which may result in different dog sizes) create a list of booleans with a
        number of Trues equal to the dogSize"""

        # Predefined values according to the rules
        dogSize = self.dogSizes[self.playerCount]
        # 78 is the total number of cards and 3 the number of cards given to a player at once, in an IRL game the
        # nbOfDeals would represent the number of times a dealer has to take cards from the deck and put them somewhere
        # else, either in a players hand or into the dog. In this function it represents the length of the deals list.
        nbOfDeals = int((78 - dogSize) / 3 + dogSize)
        deals = [False for _ in range(nbOfDeals)]

        # Loop in which some deals become "dog-deals", meaning that the cards go into the dog and not into a players
        # hand. This is random but has to comply to the following rules:
        for _ in range(dogSize):
            # Don't replace a True with a True, don't have a True beside another True,
            # don't have a leading or an ending True
            i = 0
            while deals[i] or deals[i + 1] or deals[i - 1] or i == 0:
                i = randint(1, len(deals) - 2)
            deals[i] = True

        return deals

    def awaitContracts(self):
        for i in range(self.playerCount):
            self.players[self.dealer - i - 1].chooseContract()


class Player:
    def __init__(self, name):
        # VALIDATE PARAMETERS
        self.name = name

        # INITIALIZE VARIABLES
        self.hand = []

    def rename(self, name):
        self.name = name

    def addCardsToHand(self, cards: list) -> None:
        for card in cards:
            self.hand.append(card)

    def chooseContract(self):
        print(self.name)


class GameException(Exception):
    """Class for errors"""


if __name__ == '__main__':
    game = Game(4)
    game.start()
    print()
    game2 = Game(5, lastDealer=3)
    game2.start()
    print()
    game3 = Game(3)
    game3.start()
