import random as rd
from typing import List
from tarotExceptions import GameException, PlayerException

# TODO: add a toggleable print function for more information when 'human' playing
# TODO: utils function for x.pop(x.index(y)
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
    # Information about the number of cards necessary to be able to announce a handful
    handfulSizes = {
        3: (13, 15, 18),
        4: (10, 13, 15),
        5: (8, 10, 13)
    }
    # Every card of a suit paired of an integer in increasing order
    cardNameToValue = {
        "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
        "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
        "J": 11, "C": 12, "Q": 13, "K": 14
    }
    # All the possible contracts
    contracts = ['pass', 'small', 'guard', 'guard w/o', 'guard against']

    def __init__(self, players=4, deck=None, matchPoints=None, lastDealer=None):
        """Validate parameters and initialize variables"""  # TODO: initial docstring describes class not initializer

        # VALIDATE PARAMETERS
        # PARAM PLAYERS: is limited to specific values as described by the following error message:
        paramPlayersExceptionString = "Parameter players has to be a integer in [3, 4, 5] or a list of Player objects"
        # If Players have to be created
        if type(players) is int:
            if players not in [3, 4, 5]:
                raise GameException(paramPlayersExceptionString)
            self.players: List[Player] = [Player(name=f'Player {n}', strategy=MODE) for n in range(players)]

        # If the Players already existed
        elif type(players) is list:
            if any([player is not Player for player in players]) or len(players) not in [3, 4, 5]:
                raise GameException(paramPlayersExceptionString)
            self.players: List[Player] = players
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

        # If a player has to show a card
        self.showedCards = [[]] * self.playerCount

        # Information about the contract chosen by the taker
        self.highestContract = 'pass'
        self.playerTaking = None

        # In a game with five players, the taker calls for a teammate
        self.calledCard = None

        # If exists, player who called a chelem:
        self.chelemPlayer = None

        # If wanted and possible, players can call a handful
        self.handfuls = [None] * self.playerCount

        # There are as many tricks in a game then there are cards in a player's hand
        self.nTricks = int((78 - self.dogSizes[self.playerCount]) / self.playerCount)

        # To keep track of a trick's winner, who'll be the startingPlayer of a next trick
        self.startingPlayer = None

        # History of past tricks and current trick
        self.tricks: List[list] = []

        # The player who played the excuse
        self.excusePlayer: int = None
        # The player to whom the player playing the excuse ows a card, because this player won the trick the excuse was
        # played in
        self.owsExcuseCard: int = None

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
        """Start the execution of the different phases in the game"""

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
        for i in range(self.playerCount):
            currentPlayer = self.dealer - i - 1
            if self.players[currentPlayer].callChelem():
                # Get the position of the player who called the Chelem
                self.chelemPlayer = self.players.index(self.players[currentPlayer])
                # Only the first one to announce a Chelem can do it, no other player after
                break

        # Let each player announce a handful starting from the one to the right of the dealer and then in a
        # counter-clockwise order, if
        for i in range(self.playerCount):
            currentPlayer = self.dealer - i - 1
            if handful := self.players[currentPlayer].callHandful() is not None:
                self.handfuls[currentPlayer] = handful

        # In a game there are as many tricks left to play, then there are cards in a player's hand
        # Play the number of tricks required
        for nTrick in range(self.nTricks):
            print('next trick')
            self._playTrick(nTrick)

        for player in self.players:
            print("END", "player:", player.name, player.cardsWon)

    def _deal(self):
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
        """Change the dealer when re-dealing the cards and any other action starting at a position relative to the
        dealer"""

        self.dealer -= 1
        if self.dealer < 0:
            self.dealer = self.playerCount - 1

    def _awaitContracts(self) -> None:
        """Get the desired contract from every player in the game"""

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
        """Take all the cards back from the player's hands and the dog and put them back together to form a new deck"""

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

    def showCards(self, activePlayer, cards: list):
        """Add cards to a public variable for all players to see and remember which cards the activePlayer had to show."""

        self.showedCards[activePlayer].extend(cards)

    def _playTrick(self, n: int) -> None:
        """Let every player play a card, validating that the card can be played. Then give the won cards to the right
        player"""

        # Start a new trick in the game's history
        self.tricks.append([''] * self.playerCount)

        # In the first trick, the startingPlayer for this trick is the person to the right of the dealer
        # Exception if a player has called a Chelem, in that case, this player starts
        if n == 0:
            if self.chelemPlayer is None:
                self.startingPlayer = self.dealer - 1
            else:
                self.startingPlayer = self.chelemPlayer

        # Starting from the startingPlayer and in counter-clockwise order
        for i in range(self.playerCount):
            currentPlayer = self.startingPlayer - i

            # Get the mainCard for the trick to determine which other cards can be played by the following players
            mainCard: str = None
            # Only works when the card has already been played, so after the first card
            if i > 0:
                # Get the first card from the n^th trick if it isn't the Excuse
                if self.tricks[n][self.startingPlayer] == 'EX':
                    if i > 1:
                        startingPlayerIndex = self.startingPlayer - 1
                        mainCard = self.tricks[n][startingPlayerIndex]
                else:
                    mainCard = self.tricks[n][self.startingPlayer]

            # If existing, find the highest trump played in the current trick
            trumps = sorted([card for card in self.tricks[n] if 'T' in card])
            try:
                highestTrump = int(trumps[0][:-1])
            except IndexError:
                highestTrump = None

            playedCard = self.players[currentPlayer].playCard(mainCard, highestTrump)
            self.tricks[n][currentPlayer] = playedCard

        # Set a startingPlayer for the next trick
        trickWinner = self._getTrickWinner(n)
        self.startingPlayer = trickWinner

        # Give the cards of the trick to whoever should get them
        self.giveBackCardsOfAWonTrick(n, trickWinner)

    def _getTrickWinner(self, n: int) -> int:
        """Find which player has played the card that won the trick."""

        # Get the current trick from the trick history
        trick: List[str] = self.tricks[n]

        # Get the mainCard for the trick
        # The mainCard is the first card played, except if the excuse has been played where the mainCard becomes the
        # second card played
        if trick[self.startingPlayer] == 'EX':
            startingPlayerIndex = self.startingPlayer - 1
            mainCard = trick[startingPlayerIndex]
        else:
            mainCard = trick[self.startingPlayer]
        mainCardValue, mainCardType = mainCard[:-1], mainCard[-1]

        # Check if any card in the trick is a trump
        trumpsInTrick = [card for card in trick if 'T' in card]
        # If that is the case, the highest trump wins the trick
        if len(trumpsInTrick) > 0:
            # Find the highest trump in the list of trumps
            winningCard = sorted(trumpsInTrick, key=lambda s: int(s[:-1]))[-1]

        # If there are no trumps in the trick, the winningCard is the highest one of the mainCard's suit
        else:
            # Get all the cards of the mainCard's suit
            cardsOfMainCardsSuitInTrick = [card for card in trick if mainCardType in card]
            # Find the card with the highest value
            winningCard = sorted(cardsOfMainCardsSuitInTrick, key=lambda s: Game.cardNameToValue[s[:-1]])[-1]

        # If a player who has announced a Chelem plays the excuse in the last trick, he wins the trick
        if self.nTricks - 1 == n and self.chelemPlayer is not None and trick[self.chelemPlayer] == 'EX':
            winningCard = 'EX'

        return trick.index(winningCard)

    def giveBackCardsOfAWonTrick(self, n: int, trickWinner: int):
        """Give the cards to the winner, and handle situations in which the cards go to other players"""

        # Get all the cards that were played in the trick
        trick = self.tricks[n].copy()

        # Return the excuse to its initial owner if the excuse has been played in this trick and if this isn't the last
        # trick
        if 'EX' in trick and self.nTricks - 1 != n:
            # Get the identity of the player in the Game.players list
            self.excusePlayer = trick.index('EX')
            # If the player who played the excuse is not already getting back his card (so that he doesn't ow himself a
            # card)
            if self.excusePlayer != trickWinner:
                # Give back the card
                self.players[self.excusePlayer].takeCardsWon([trick.pop(self.excusePlayer)])
                # Memorize whom the person that played the excuse ows a card
                self.owsExcuseCard = trickWinner

        # After the excuse has been given to the right person, the rest of the trick goes to its winner
        self.players[trickWinner].takeCardsWon(trick)

        # But the player who played the excuse ows a 1/2 point card to the player that won the trick in which the
        # excuse was played  # TODO: if (at the end of the game / during the game), the card wasn't given, a player of the same team gives one
        # If there is a player to whom a card is owed
        if self.owsExcuseCard is not None:
            # Get all the cards that have a value of 1/2 point
            halfAPointCards = [card for card in self.players[self.excusePlayer].cardsWon
                               if 'EX' not in card and '1T' not in card and '21T' not in card and
                               ('T' in card or Game.cardNameToValue[card[:-1]] <= 10)]
            # If there is a card that can be given
            if len(halfAPointCards) > 0:
                # Give that card from the players own stack and put it into the other players stack
                excusePlayerCardsWon = self.players[self.excusePlayer].cardsWon
                owedCard = excusePlayerCardsWon.pop(excusePlayerCardsWon.index(halfAPointCards[0]))
                self.players[self.owsExcuseCard].takeCardsWon([owedCard])
                # No card is owed anymore
                self.owsExcuseCard = None

    def end(self) -> tuple:  # TODO: export data for following game
        """Returns all information that is needed to start a new game with the already existing deck and players"""
        # TODO: The deck can be gotten from the history of tricks as to ensure the order of the cards, add the dog to the
        # beginning and put the cards of the players into the deck team after team (if there are some)

        return ()


class Player:
    def __init__(self, name: str, strategy: str):
        """Validate parameters and initialize variables"""

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
        """Change the name of a player"""

        self.name = str(name)

    def joinGame(self, gameObject: Game):
        """Link a Game object to the player"""

        self.game = gameObject

    def _getDecision(self, question: str, options: List[str]) -> str:
        """Given an answer and set of possible options, a player has to decide which option to choose."""

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
        """Add cards to a player's hand"""

        self.hand.extend(cards)
        if sort:
            self.hand.sort(key=self._handSortKey)

    def _handSortKey(self, s: str) -> str:
        """Allows sorting of the cards in the same order as they were dealt"""

        return Game.create_deck().index(s)

    def clearHand(self) -> [str]:
        """Empties a player's hand and returns the cards that were in it"""

        oldHand, self.hand = self.hand.copy(), []
        return oldHand

    def takeCardsWon(self, cards: list):
        """Transfers the cards into the stack of cards won by the player"""

        if 'EX' in cards:
            print("HEY!! EX")
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

        # The excuse cannot be put into the aside
        if 'EX' in options:
            options.remove('EX')

        # Compare the number of cards missing in the aside to the number cards that are not trumps
        missingInAsideCount = Game.dogSizes[self.game.playerCount] - len(self.cardsWon)
        notTrumpsInHand = [option for option in options if 'T' not in option]

        # If there are more or exactly enough cards that are not trumps, then the number of cards missing in the aside
        if len(notTrumpsInHand) >= missingInAsideCount:
            # Remove all the trumps from the options
            trumpsInHand = [option for option in options if 'T' in option]
            for trump in trumpsInHand:
                options.remove(trump)

        # Get decision from player
        card = self._getDecision(question, options)

        # If a player decides to put a trump into his aside, he has to show it to the other players
        if 'T' in card:
            self.game.showCards(self.game.players.index(self),
                                [card])

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

    def callHandful(self):
        """Let the player decide (if possible) whether they want to announce a handful"""

        # Get the number of trumps in the player's hand and how many are needed for calling the handfuls
        trumpsInHand = [card for card in self.hand if 'T' in card or 'EX' in card]
        trumpsNeededForHandful = Game.handfulSizes[self.game.playerCount]

        question = "Do you want to call a handful?"
        options = ['Simple handful', 'Double handful', 'Triple Handful']

        # Eliminate the options that aren't possible
        if len(trumpsInHand) >= trumpsNeededForHandful[0]:
            options = options[0:1]
        elif len(trumpsInHand) >= trumpsNeededForHandful[1]:
            options = options[:2]
        elif len(trumpsInHand) >= trumpsNeededForHandful[2]:
            options = options
        else:
            return None

        # Add the possibility not to call the handful
        options.append("Don't call handful")

        # Get decision from player
        decision = self._getDecision(question, options)

        # If the player decides not to call, the handful returns the same as if it wasn't possible
        if decision == "Don't call handful":
            return None

        # Show the cards you have in a handful, starting from the lowest value one, until you showed all necessary ones,
        # including at last if available the excuse
        trumpsInHandSorted = sorted(trumpsInHand, key=self._handSortKey)
        self.game.showCards(self.game.players.index(self),
                            [trumpsInHandSorted[i] for i in range(trumpsNeededForHandful[options.index(decision)])])

        return decision

    def playCard(self, mainCard: str, highestTrump: int):
        """Make the player choose one of the cards in his hand to play in the trick"""

        # Define the question
        question = "Which card do you want to play in this trick?"

        # Base options are all the cards in the player's hand
        options = self.hand.copy()

        # If the first card of the trick has already been played, limit the options the player has according to
        # this card
        if mainCard is not None:
            mainCardValue, mainCardType = mainCard[:-1], mainCard[-1]

            # If the mainCard is part of a suit
            if mainCardType in ['♤', '♡', '♧', '♢']:
                # Check if the player has a card of the required suit in his hand
                cardOfMainCardSuitInHand = [option for option in options if mainCardType in option]
                # If this is the case, all cards of the same suit can be played, and no other card
                if len(cardOfMainCardSuitInHand) > 0:
                    options = cardOfMainCardSuitInHand
                # If this isn't the case, the player has to play a trump
                else:
                    mainCardType = 'T'

            # If the mainCard is a trump
            if mainCardType == 'T':
                # If any trumps have already been played in the trick
                if highestTrump is not None:
                    # Check if the player has a trump over the current highest trump in his hand
                    trumpsOverHighestTrumpInHand = [option for option in options
                                                    if mainCardType in option
                                                    and int(option[:-1]) < highestTrump]
                # Else, there cannot be any trumps over a non-existing highestTrump, so we roll over to the next case,
                # where any trump can be played
                else:
                    trumpsOverHighestTrumpInHand = []
                # If this is the case, all trumps over the current highest trump can be played
                if len(trumpsOverHighestTrumpInHand) > 0:
                    options = trumpsOverHighestTrumpInHand
                # If this isn't the case, the player has to play any other trump he has
                else:
                    # Check if the player has any trump in his hand
                    trumpsInHand = [option for option in options if mainCardType in option]
                    # If this is the case, all trumps can be played
                    if len(trumpsInHand) > 0:
                        options = trumpsInHand
                    # If this isn't the case, the player has to play any other leftover card, which was already
                    # specified in the beginning of the function

        # Always allow a player to play the excuse if he has it
        if 'EX' in self.hand:
            options.append('EX')

        # Get the card the player plays
        card = self._getDecision(question, options)
        self.hand.pop(self.hand.index(card))
        return card


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
    print('total:', TOTALTIME, 'average:', TOTALTIME / tests)
