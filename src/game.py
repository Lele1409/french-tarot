import random as rd
from tarotExceptions import GameException, PlayerException

# TODO: add a toggleable print function for more information when 'human' playing
MODE = 'random'


class Game:
    # Information about the number of cards in the dog
    dogSizes = {
        3: 6,
        4: 6,
        5: 3
    }
    # Information about the number of cards dealt at once to a player
    dealSizes = {
        3: 4,
        4: 3,
        5: 3
    }
    # All the possible contracts
    contracts = ['pass', 'small', 'guard', 'guard w/o', 'guard against']

    def __init__(self, players=4, deck=None, matchPoints=None, lastDealer=None):
        # VALIDATE PARAMETERS
        # PARAM PLAYERS: is limited to specific values as described by the following error message:
        paramPlayersExceptionString = "Parameter players has to be a int in [3, 4, 5] or a list of Player objects"
        # If Players have to be created
        if type(players) is int:
            if players not in [3, 4, 5]:
                raise GameException(paramPlayersExceptionString)
            self.players = [Player(name=f'Player {n}', strategy=MODE) for n in range(players)]

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
            deck = self.create_deck()
            rd.shuffle(deck)
        if type(deck) is list and sorted(deck) == sorted(self.create_deck()):
            self.deck = deck
        else:
            raise GameException(f"""Parameter deck has to be a list of strings, where the strings have to be the same 
                                 as in a newly generated deck""")

        # PARAM LASTDEALER: can be set from previous game, making the dealer change by one player
        if lastDealer is None:
            self.dealer = rd.randint(0, self.playerCount - 1)
        elif type(lastDealer) is int and lastDealer in range(0, self.playerCount + 1):
            self.dealer = lastDealer
            self._nextDealer()
        else:
            raise GameException(f"Parameter lastDealer has to be None or a integer in range(0, {self.playerCount + 1})")

        # INITIALIZE VARIABLES
        # A list containing the cards in the dog
        self._dog = []
        self.dog = []  # Cards transferred from self._dog to self.dog if all players know the cards that were in the dog
        self.aside = []  # If a player has to show a card that he puts into his aside

        # Information about the contract chosen by the taker
        self.highestContract = 'pass'
        self.playerTaking = None

        # Five player game, the taker calls for a teammate
        self.calledCard = None

        # If exists, player who called a chelem:
        self.chelemPlayer = None

    @staticmethod
    def create_deck() -> list:  # TODO: memoization??
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

    def play(self):
        # Make the players choose a contract after the cards are dealt to them
        # If no contract is chosen, start over by re-dealing
        while self.highestContract == 'pass':
            self._deal()
            self._awaitContracts()

        if self.playerCount == 5:
            self.calledCard = self.players[self.playerTaking].callPlayer()

        # Give the dog to the player that is taking or to the defendants
        self._convertDogToAside()

        # Give each player starting from the one to the right of the dealer and then in a counter-clockwise order the
        # opportunity to announce a Chelem, only one player can announce a Chelem
        i = self.dealer - 1
        for _ in range(self.playerCount):
            if i < 0:
                i = self.playerCount - 1
            if self.players[i].callChelem():
                self.chelemPlayer = i
                break
            i -= 1

        # Let each player announce a handful


        # Play tricks (param trick:int)  # TODO: starting player to the right of the dealer or player who called chelem
        # n = (78 - sizeofdog) / nbPlayers = len(player.hand)
        print('PLAYING TRICKS')

    def _deal(self):  # TODO: add start deal at right of dealer
        """Get a list of booleans. For every boolean value, if True a card is put into the dog if False three cards
        are given to the next player starting at the player next to the dealer"""

        # The deck gets cut at some random place, but not closer to the ends of the deck than the size of a deal
        # to a player
        deckCutIndex = rd.randint(0 + Game.dealSizes[self.playerCount],
                                  len(self.deck) - 1 - Game.dealSizes[self.playerCount])
        self.deck = self.deck[deckCutIndex:] + self.deck[:deckCutIndex]

        # List of booleans specifying the deal type
        deals = self._getDealOrder()

        nextPlayer = self.dealer - 1
        for deal in deals:
            # If a deal equals to True, it is meant to go into the dog
            if deal == True:  # NOQA
                # Add the first card of the deck to the dog
                self._dog.append(self.deck.pop(0))

            # Else if a deal equals to False, it is meant to be dealt to a player
            else:
                # If the index goes too far, rollover to the other end
                if nextPlayer < 0:
                    nextPlayer = self.playerCount - 1

                # Give the three first cards of the deck to the next player
                cardsDealt = [self.deck.pop(0) for _ in range(Game.dealSizes[self.playerCount])]
                self.players[nextPlayer].addCardsToHand(cardsDealt, sort=False)

                # Set the nextPlayer to what would be the player to the right of the current player
                nextPlayer -= 1

        # Repeat this function recursively until no player gets a hand containing: only the first trump ('1T') and not
        # the excuse ('EX')
        for player in self.players:
            if '1T' in player.hand and 'EX' not in player.hand:
                if len([card for card in player.hand if 'T' in card]) == 1:
                    self._resetDeck()
                    self._deal()

    def _getDealOrder(self) -> list:
        """Depending on the playerCount (which may result in different dog sizes) create a list of booleans with a
        number of Trues equal to the dogSize"""

        # Predefined values according to the rules
        dogSize = Game.dogSizes[self.playerCount]
        # 78 is the total number of cards and 3 the number of cards given to a player at once, in an IRL game the
        # nbOfDeals would represent the number of times a dealer has to take cards from the deck and put them somewhere
        # else, either in a player hand or into the dog. In this function, it represents the length of the deal list.
        nbOfDeals = int((78 - dogSize) / Game.dealSizes[self.playerCount] + dogSize)
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
            chosenContract = self.players[currentPlayer].chooseContract()
            # Update the instance fields if the chosen contract is higher than the one highest before
            if chosenContract != 'pass':
                self.highestContract = chosenContract
                self.playerTaking = currentPlayer

        # Re-deal if no one chose a contract
        if self.highestContract == 'pass':
            self._resetDeck()

    def _resetDeck(self):
        # For every player
        for i in range(self.playerCount):
            # Reset the player's hands and get back the cards in the following order:
            # start from the right of the dealer and in counter-clockwise order (just as during the deal)
            self.deck.extend(self.players[self.dealer - i - 1].clearHand())
        # Finally, add back the dog to the deck and empty it
        self.deck.extend(self._dog)
        self._dog = []

    def _convertDogToAside(self) -> None:
        """Transfer the cards of the dog to whatever player should get it"""
        player = self.players[self.playerTaking]

        # If the taker takes with a 'small' or a 'guard' contract, he gets the cards into his hand and has to put back
        # the same number of cards into his aside (same as Player.cardsWon since the cards are part of the players final
        # points)
        if self.highestContract in Game.contracts[1:3]:
            player.addCardsToHand(self._dog)

            # The cards are shown to the other players (not the case if 'guard w/o' or 'guard against')
            self.dog = self._dog
            self._dog = []

            for _ in range(Game.dogSizes[self.playerCount]):
                player.putCardInAside()

        # In case the contract is a 'guard w/o' the player taking takes the card from the dog without looking at
        # them
        elif self.highestContract == Game.contracts[3]:
            player.takeCardsWon(self._dog)

        # In case the contract is a 'guard against' the points of the dog are given to the Defence at the end of the
        # game
        elif self.highestContract == Game.contracts[4]:
            self.guardAgainstCards = self._dog

    def showCardsInAside(self, cards: list):
        self.aside.extend(cards)

    def end(self) -> tuple:  # TODO: export data for following game
        # Returns all information that is needed to start a new game with the already existing deck and players
        pass


class Player:
    def __init__(self, name: str, strategy: str):
        # VALIDATE PARAMETERS
        # A name to easily identify the players or the order in which they sit in
        self.name = str(name)

        validStrategies = ['human', 'random']
        if strategy in validStrategies:  # TODO: (LONG TERM) MORE STRATEGIES (AI)
            self.strategy = strategy
        else:
            raise PlayerException("Please use one of the following strategies:", validStrategies)

        # INITIALIZE VARIABLES
        self.hand = []

        self.cardsWon = []

        self.game: Game = None

        self.calledCard = None

    def rename(self, name) -> None:
        self.name = str(name)

    def joinGame(self, gameObject: Game):
        self.game = gameObject

    def _getDecision(self, question: str, options: [str]) -> str:
        # Validate the format of the possible options
        if any([type(element) is not str for element in options]) or len(options) == 0:
            raise PlayerException("Parameter 'options' in 'decide' only takes a list of strings")

        # Show the question to the user if the user is a human player and return the option chosen by the player
        if self.strategy == 'human':
            print(f"{self.name} hand: {sorted(self.hand, key=self._handSortKey)}:")
            print(question)

            playerAnswer = None
            while playerAnswer not in options:
                print(f"Please enter one of the following options {options}:")
                playerAnswer = input()

            return playerAnswer

        # Return a randomly chosen option
        elif self.strategy == 'random':
            return rd.choice(options)

    def addCardsToHand(self, cards: list, sort=False) -> None:
        self.hand.extend(cards)
        if sort:
            self.hand.sort(key=self._handSortKey)

    def _handSortKey(self, s: str) -> str:
        return Game.create_deck().index(s)

    def clearHand(self) -> [str]:
        """Empties a player's hand and returns the cards that were in it"""
        oldHand, self.hand = self.hand.copy(), []
        return oldHand

    def takeCardsWon(self, cards: list):
        self.cardsWon.extend(cards)

    def putCardInAside(self) -> None:
        """Ask the player to choose which cards we would like to transfer from his hand to the aside, keeping in mind
         the limitations when doing so"""
        # Define the question
        question = f"Choose a card in your hand to put into your aside."

        # Select the options
        options = self.hand.copy()
        # Kings cannot be put into the aside
        for king in [option for option in options if 'K' in option]:
            options.remove(king)

        # Compare the number of cards missing in the aside to the number no not trump cards
        missingInAsideCount = Game.dogSizes[self.game.playerCount] - len(self.cardsWon)
        notTrumpsInHand = [option for option in options if 'T' not in option]

        # If there are fewer cards that aren't trumps then the number of cards missing in the aside
        if len(notTrumpsInHand) >= missingInAsideCount:
            # Remove all the trumps from the options
            trumpsInHand = [option for option in options if 'T' in option]
            for trump in trumpsInHand:
                options.remove(trump)

        # The excuse cannot be put into the aside
        if 'EX' in options:
            options.remove('EX')

        # Get decision from player
        card = self._getDecision(question, options)

        # If a player decides to put a trump into his aside, he has to show it to the other players
        self.game.showCardsInAside([card])

        self.cardsWon.append(self.hand.pop(self.hand.index(card)))

    def chooseContract(self) -> str:
        """Let the player choose one of the available contracts, if no contract is left available"""
        highestContract = self.game.highestContract
        highestContractIndex = Game.contracts.index(highestContract)
        leftoverOptions = ['pass'] + Game.contracts[highestContractIndex + 1:]
        if len(leftoverOptions) > 1:
            contract = self._getDecision("Choose a contract.", leftoverOptions)
            return contract
        else:
            return 'pass'

    def callPlayer(self) -> str:
        """In the five-player variant of the game, the caller has to call a king before taking the dog. The player who
        holds that card now plays with the caller in a team."""
        question = "Please call a card, whoever has this card will be your partner."

        options = []

        # Can be called:
        #  - Any king (even if the player has this king himself)
        options.extend([card for card in Game.create_deck() if 'K' in card])

        #  - If a player has all Kings, he can call a Queen. The same goes for the Queen, the Cavalryman and the Jack
        i = 0
        value = ['K', 'Q', 'C', 'J']
        while len([card for card in self.hand if value[i] in card]) == 4 and i < 4:
            options.extend([card for card in self.hand if value[i] in card])
            i += 1

        calledCard = self._getDecision(question, options)
        return calledCard

    def callChelem(self) -> bool:
        """Let the player decide if he wants to try a Chelem or not"""
        chelemQuestion = "Are you calling a Chelem?"
        chelemOptions = ['Chelem', 'no Chelem']
        if self._getDecision(chelemQuestion, chelemOptions) == 'Chelem':
            return True
        else:
            return False


if __name__ == '__main__':
    import time
    # game = Game(3)
    # game.play()
    # print()
    # game2 = Game(4, lastDealer=3)
    # game2.play()
    # print()
    # game3 = Game(5)
    # game3.play()

    # exit()
    games = 0  # NOQA
    tests = 1e7
    TOTALSTART = time.perf_counter_ns()
    while games < tests:
        start = time.perf_counter_ns()
        game = Game(rd.randint(3, 5), lastDealer=rd.randint(0, 3))
        game.play()
        singleTime = time.perf_counter_ns() - start
        print(singleTime, games)
        games += 1
    TOTALTIME = time.perf_counter_ns() - TOTALSTART
    print('total:', TOTALTIME, 'average:', TOTALTIME/tests)
