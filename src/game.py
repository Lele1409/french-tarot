import random as rd


class Game:  # TODO: in a 3 player game, cards are dealt four at a time
    # Information about the number of cards in the dog
    dogSizes = {
        3: 6,
        4: 6,
        5: 3
    }
    # All the possible contracts
    contracts = ['pass', 'small', 'guard', 'guard w/o', 'guard against']

    # noinspection SpellCheckingInspection
    def __init__(self, players=4, deck=None, matchPoints=None, lastDealer=None):
        # VALIDATE PARAMETERS
        # PARAM PLAYERS: is limited to specific values as described by the following error message:
        paramPlayersExceptionString = "Parameter players has to be a int in [3, 4, 5] or a list of Player objects"
        # If Players have to be created
        if type(players) is int:
            if players not in [3, 4, 5]:
                raise GameException(paramPlayersExceptionString)
            self.players = [Player(name=f'Player {n}', strategy='human') for n in range(players)]

        # If the Players already existed
        elif type(players) is list:
            if any([player is not Player for player in players]) or len(players) not in [3, 4, 5]:
                raise GameException(paramPlayersExceptionString)
            self.players = players
        else:
            raise GameException(paramPlayersExceptionString)

        self.playerCount = len(self.players)

        # Make all the players able to access the game data by pointing at this instance of the Game object
        for player in self.players:
            player.joinGame(self)

        # PARAM MATCHPOINTS: set scores if this is the first game in a match
        if matchPoints is None:
            matchPoints = [0 * self.playerCount]
        self.matchPoints = matchPoints

        # PARAM DECK: can be set from previous game, or a new deck will be created and shuffled
        if deck is None:
            deck = self._create_deck()
            rd.shuffle(deck)
        self.deck = deck

        # PARAM LASTDEALER: can be set from previous game, making the dealer change by one player
        if lastDealer is None:
            self.dealer = 0
        elif type(lastDealer) is int and lastDealer in range(0, self.playerCount + 1):
            self.dealer = lastDealer
            self._nextDealer()
        else:
            raise GameException("Parameter lastDealer has to be None or a integer in range()")

        # INITIALIZE VARIABLES
        # A list containing the cards in the dog
        self._dog = []
        self.dog = []  # Cards transferred from self._dog to self.dog if all players know the cards that were in the dog

        # Information about the contract chosen by the taker
        self.highestContract = 'pass'
        self.playerTaking = None

    def _create_deck(self) -> list:
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
        # Make the players choose a contract after the cards are dealt to them
        # If no contract is chosen, start over by re-dealing
        while self.highestContract == 'pass':
            self._deal()
            self._awaitContracts()

        # Give the dog to the player that is taking or to the defendants
        self._dogToAside()

        # play tricks (param trick:int)
        print('PLAYING FIRST TRICK')

    def _deal(self):  # TODO: add start deal at right of dealer
        """Get a list of booleans. For every boolean value, if True a card is put into the dog if False three cards
        are given to the next player starting at the player next to the dealer"""

        # The deck gets cut at some random place, but not closer to the ends of the deck than the size of a deal
        # to a player
        deckCutIndex = rd.randint(0 + 3, len(self.deck) - 1 - 3)
        self.deck = self.deck[deckCutIndex:] + self.deck[:deckCutIndex]

        # List of booleans specifying the deal type
        deals = self._specifyDealOrder()

        nextPlayer = 0
        for deal in deals:
            if deal == True:  # NOQA | if the card is for the dog
                # Add the first card of the deck to the dog
                self._dog.append(self.deck.pop(0))
            else:
                # Give the three first cards of the deck to the next player
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
        dogSize = Game.dogSizes[self.playerCount]
        # 78 is the total number of cards and 3 the number of cards given to a player at once, in an IRL game the
        # nbOfDeals would represent the number of times a dealer has to take cards from the deck and put them somewhere
        # else, either in a player hand or into the dog. In this function, it represents the length of the deal list.
        nbOfDeals = int((78 - dogSize) / 3 + dogSize)
        deals = [False for _ in range(nbOfDeals)]

        # Loop in which some deals become "dog-deals" meaning that the cards go into the dog and not into a player's
        # hand. This is random but has to comply with the following rules:
        for _ in range(dogSize):
            # Don't replace a True with a True, don't have a True beside another True,
            # don't have a leading or an ending True
            i = 0
            while deals[i] or deals[i + 1] or deals[i - 1] or i == 0:
                i = rd.randint(1, len(deals) - 2)
            deals[i] = True

        return deals

    def _nextDealer(self) -> None:
        self.dealer -= 1
        if self.dealer < 0:
            self.dealer = self.playerCount - 1

    def _awaitContracts(self) -> None:
        # For every player
        for i in range(self.playerCount):
            # Starting from the player to the right of the dealer, and then counter-clockwise get the contract chosen by
            # each player
            currentPlayer = self.dealer - i - 1
            chosenContract = self.players[currentPlayer].chooseContract(highestContract=self.highestContract)
            # Update the instance fields if the chosen contract is higher than the one highest before
            if chosenContract != 'pass':
                self.highestContract = chosenContract
                self.playerTaking = currentPlayer

        # Re-deal if no one chose a contract
        if self.highestContract == 'pass':
            self.resetDeck()

    def resetDeck(self):
        # For every player
        for i in range(self.playerCount):
            # Reset the player's hands and get back the cards in the following order:
            # start from the right of the dealer and in counter-clockwise order (just as during the deal)
            self.deck.extend(self.players[self.dealer - i - 1].clearHand())
        # Finally, add back the dog to the deck and empty it
        self.deck.extend(self._dog)
        self._dog = []

    def _dogToAside(self) -> None:
        """Transfer the cards of the dog to whatever player should get it"""
        # If the taker takes with a 'small' or a 'guard' contract, he gets the cards into his hand and has to put back
        # the same number of cards into his aside (same as Player.cardsWon since the cards are part of the players final
        # points)
        if self.highestContract in Game.contracts[1:3]:
            self.players[self.playerTaking].addCardsToHand(self._dog)

            # If the cards are shown to the other players (not the case if 'guard w/o' or 'guard against')
            self.dog = self._dog
            self._dog = []

            for _ in range(Game.dogSizes[self.playerCount]):
                self.players[self.playerTaking].putCardToAside()

        #
        elif self.highestContract == Game.contracts[3]:
            pass

    def end(self) -> tuple:  # TODO: export data for other game
        # Returns all information that is needed to start a new game with the already existing deck and players
        pass


class Player:
    def __init__(self, name: str, strategy: str):
        # VALIDATE PARAMETERS
        # A name to easily identify the players or the order in which they sit in
        self.name = str(name)

        validStrategies = ['human', 'random']
        if strategy in validStrategies:  # TODO: more strategies
            self.strategy = strategy
        else:
            raise PlayerException("Please use one of the following strategies:", validStrategies)

        # INITIALIZE VARIABLES
        self.hand = []
        self.cardsWon = []
        self.game = None

    def rename(self, name) -> None:
        self.name = str(name)

    def joinGame(self, gameObject: Game):
        self.game = gameObject

    def _getDecision(self, question: str, options: [str]) -> str:
        # Validate the format of the possible options
        if any([type(element) is not str for element in options]):
            raise PlayerException("Parameter 'options' in 'decide' only takes a list of strings")

        # Show the question to the user if the user is a human player and return the option chosen by the player
        if self.strategy == 'human':
            print(f"{self.name} hand: {self.hand}:")
            print(question)

            playerAnswer = None
            while playerAnswer not in options:
                print(f"Please enter one of the following options {options}:")
                playerAnswer = input()

            return playerAnswer

        # Return a randomly chosen option
        elif self.strategy == 'random':
            return rd.choice(options)

    def addCardsToHand(self, cards: list) -> None:
        self.hand.extend(cards)
        self.hand.sort(key=self.handSortKey)

    def clearHand(self) -> list:
        oldHand, self.hand = self.hand, []
        return oldHand

    def putCardToAside(self) -> None:
        """Ask the player to choose which cards we would like to transfer from his hand to the aside, keeping in mind
         the limitations when doing so"""
        # Define the question
        question = f"Choose a card in your hand to put into your aside."

        # Select the options
        options = self.hand
        # Kings cannot be put into the aside
        for king in ['K' in option for option in options]:
            options.remove(king)
        # If there are fewer cards that aren't trumps then the number of cards missing in the aside
        if len(['T' in option for option in options]) < Game.dogSizes[self.game.playerCount] - self.cardsWon:
            ...

        card = self._getDecision(question, options)
        self.cardsWon.append(self.hand.pop(self.hand.index(card)))

    def handSortKey(self, s: str) -> str:  # TODO: fix letters before numbers in suits
        if 'T' not in s and 'EX' not in s:
            # To get all the simple cards to the beginning of the list
            s = s[::-1]
            # And the face cards to the end of this sub-list
            if not s.endswith(('J', 'C', 'Q', 'K')):
                s = s
        if s == 'EX':
            pass
        else:
            s = '0' + s[:-1]
        return s

    def chooseContract(self, highestContract='pass'):
        highestContractIndex = Game.contracts.index(highestContract)
        leftoverOptions = ['pass'] + Game.contracts[highestContractIndex + 1:]
        if len(leftoverOptions) > 1:
            contract = self._getDecision("Choose a contract.", leftoverOptions)
            return contract
        else:
            return 'pass'


class GameException(Exception):
    """Class for errors"""


class PlayerException(Exception):
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
