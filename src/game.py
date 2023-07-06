import math
import random as rd
from typing import List
from src.tarotExceptions import GameException, PlayerException
from src.humanIO import printh as printh, inputh as inputh
from src.utils import printAllGameFields as debug, Memoize  # NOQA

# from line_profiler_pycharm import profile  # NOQA

# Set execution mode
MODE = 'human'
# Based on execution mode, toggle print
if MODE == 'human':
    TOGGLE_ON = True
else:
    TOGGLE_ON = False


class Game:
    # Suits for the cards
    suits = ['♤', '♡', '♧', '♢']
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
    handfulValues = {
        'Simple handful': 20,
        'Double handful': 30,
        'Triple Handful': 40
    }
    # Every card of a suit paired of an integer in increasing order
    cardNameToValue = {
        "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
        "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
        "J": 11, "C": 12, "Q": 13, "K": 14
    }
    # All the possible contracts
    contracts = ['pass', 'small', 'guard', 'guard w/o', 'guard against']
    # Multiplier linked to the contract above
    contractMultiplier = {
        'small': 1,
        'guard': 2,
        'guard w/o': 4,
        'guard against': 6
    }
    # The cardPoints needed for a taker to win
    winConditionPoints = {
        0: 56,
        1: 51,
        2: 41,
        3: 36
    }

    def __init__(self, players=4, deck=None, matchPoints=None, lastDealer=None):
        """A class for simulating a game. Can be started with its play() method."""

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
            if any([type(player) is not Player for player in players]) or len(players) not in [3, 4, 5]:
                raise GameException(paramPlayersExceptionString)
            self.players: List[Player] = players

        # If the players parameter doesn't hold an integer or a list of players
        else:
            raise GameException(paramPlayersExceptionString)

        self.playerCount = len(self.players)

        # Make all the players able to access the game data by pointing at this instance of the Game object
        for player in self.players:
            player.joinGame(self)

        # PARAM MATCHPOINTS: set scores if this is the first game in a match
        if matchPoints is None:
            matchPoints = [0] * self.playerCount
        elif len(matchPoints) != self.playerCount:
            raise GameException("elements in matchPoints must match number of players in game")
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
        # If no previous dealer is given get one randomly
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
        self.guardAgainstCards = None  # Cards transferred from the dog if contract is 'guard against'

        # If a player has to show a card
        self.showedCards = [[]] * self.playerCount

        # Information about the contract chosen by the taker
        self.highestContract = 'pass'
        self.playerTaking = None

        # In a game with five players, the taker calls for a teammate
        self.calledCard = None
        self.calledPlayer = None

        # If exists, player who called a chelem:
        self.chelemPlayer = None

        # If wanted and possible, players can call a handful
        self.handfuls = [None] * self.playerCount

        # There are as many tricks in a game then there are cards in a player's hand
        self.nTricks = int((78 - self.dogSizes[self.playerCount]) / self.playerCount)

        # History of past tricks and current trick
        self.tricks: List[list] = [[''] * self.playerCount] * self.nTricks
        self._trickWinners = {}
        self.startingPlayerForTrick = [None] * self.nTricks

        # The player who played the excuse
        self.playedExcuse: int = None
        # The player to whom the player playing the excuse ows a card, because this player won the trick the excuse was
        # played in
        self.recipientOfOwedExcuseCard: int = None

        # Points the players make
        self.wonCardPoints = [0] * self.playerCount

    def create_deck(self) -> list:
        """Return a list of the 78 cards: four suits, all trumps and the excuse"""

        suits = Game.suits
        values = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'C', 'Q', 'K']

        # Trumps, ex: "15T"
        trumps = [f"{n}T" for n in range(1, 21 + 1)]
        # Suit cards, ex: "1♤" or "K♧"
        cards = [f"{values[value]}{suits[suit]}"
                 for suit in range(len(suits))
                 for value in range(len(values))]

        # Merge, add excuse "EX"
        deck = cards + trumps + ['EX']
        return deck

    # @profile
    def play(self):
        """Start the execution of the different phases in the game"""

        # Make the players choose a contract after the cards are dealt to them
        # If no contract is chosen, start over by re-dealing
        while self.highestContract == 'pass':
            printh("Dealing the cards and asking player which contract they want to announce.")
            self._deal()
            self._awaitContracts()

        # When a player has chosen a contract, the cards can be sorted for better playability
        for player in self.players:
            player.sortHand()

        # In a 5-player game, let the taker call a card
        if self.playerCount == 5:
            self.calledCard = self.players[self.playerTaking].callPlayer()

        # Give the dog to the player that is taking or to the defendants
        self._convertDogToAside()

        # Give the taker the opportunity to announce a Chelem
        if self.players[self.playerTaking].callChelem():
            # Get the position of the player who called the Chelem
            self.chelemPlayer = self.players.index(self.players[self.playerTaking])

        # Let each player announce a handful starting from the one to the right of the dealer and then in a
        # counter-clockwise order, if
        for i in range(self.playerCount):
            currentPlayer = self.dealer - i - 1
            # Ask the player if he wants to announce a handful (if he has one)
            handful = self.players[currentPlayer].callHandful()
            if handful is not None:
                self.handfuls[currentPlayer] = handful

        # In a game there are as many tricks left to play, then there are cards in a player's hand
        # Play the number of tricks required
        for nTrick in range(self.nTricks):
            self._playTrick(nTrick)

        # Calculate the points for every player at the end of the game
        self.countPoints()

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

        playerToGetCards = self.dealer - 1
        for deal in deals:
            # If a deal equals to True, it is meant to go into the dog
            if deal == True:  # NOQA
                # Add the first card of the deck to the dog
                self._dog.append(self.deck.pop(0))

            # Else if a deal equals to False, it is meant to be dealt to a player
            else:
                # If the index goes too far, rollover to the other end
                if playerToGetCards < 0:
                    playerToGetCards = self.playerCount - 1

                # Give the three first cards of the deck to the next player
                cardsDealt = [self.deck.pop(0) for _ in range(Game.dealSizes[self.playerCount])]
                self.players[playerToGetCards].addCardsToHand(cardsDealt, sort=False)

                # Set the playerToGetCards to what would be the player to the right of the current player
                playerToGetCards -= 1

        # Repeat the function recursively until no player gets a hand containing:
        # only the first trump ('1T') and not the excuse ('EX')
        for player in self.players:
            if '1T' in player.hand and 'EX' not in player.hand:
                if len([card for card in player.hand if 'T' in card]) == 1:
                    printh(f"{player.name} has only the petit as trump, re-dealing the cards.")
                    self._resetDeck()
                    self._nextDealer()
                    self._deal()
                    break

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
        """Change the dealer to the person to their right"""

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
                self.playerTaking = self.players.index(self.players[currentPlayer])

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
            printh(f"{player.name} takes the dog containing the following cards: {self._dog}")

            # The visible cards are in self.dog
            self.dog = self._dog.copy()

            for _ in range(Game.dogSizes[self.playerCount]):
                player.putCardInAside()

        # In case the contract is a 'guard w/o' the player taking takes the card from the dog without looking at
        # them
        elif self.highestContract == Game.contracts[3]:
            player.giveCardsWon(self._dog)

        # In case the contract is a 'guard against' the points of the dog are given to the Defence at the end of the
        # game
        elif self.highestContract == Game.contracts[4]:
            self.guardAgainstCards = self._dog.copy()

    def showCards(self, activePlayer, cards: list):
        """Add cards to a public variable for all players to see and remember which cards the activePlayer had to show."""

        # When human-playing, show the cards literally
        printh(f"{self.players[activePlayer].name} shows the following cards to everyone: {cards}")

        # Store the cards as showed
        self.showedCards[activePlayer].extend(cards)

    # @profile
    def _playTrick(self, n: int) -> None:
        """Let every player play a card, validating that the card can be played. Then give the won cards to the right
        player"""

        # In the first trick, the startingPlayer for this trick is the person to the right of the dealer
        # Exception if a player has called a Chelem, in that case, this player starts
        if n == 0:
            if self.chelemPlayer is None:
                self.startingPlayerForTrick[n] = self.dealer - 1
            else:
                self.startingPlayerForTrick[n] = self.chelemPlayer

        # Display start of a trick when human-playing
        printh(f"Start of trick {n + 1}. {self.players[self.startingPlayerForTrick[n]].name} is first to play.")

        # Starting from the startingPlayerForTrick and in counter-clockwise order
        for i in range(self.playerCount):
            currentPlayer = self.startingPlayerForTrick[n] - i

            # Get the mainCard for the trick to determine which other cards can be played by the following players
            mainCard: str = None
            # Only works when the card has already been played, so after the first card
            if i > 0:
                # Get the first card from the n^th trick if it isn't the Excuse
                if self.tricks[n][self.startingPlayerForTrick[n]] == 'EX' and i > 1:
                    startingPlayerIndex = self.startingPlayerForTrick[n] - 1
                    mainCard = self.tricks[n][startingPlayerIndex]
                else:
                    mainCard = self.tricks[n][self.startingPlayerForTrick[n]]

            # If existing, find the highest trump played in the current trick
            trumps = sorted([card for card in self.tricks[n] if 'T' in card])
            try:
                highestTrump = int(trumps[0][:-1])
            except IndexError:
                highestTrump = None

            # Get the card from the player
            playedCard = self.players[currentPlayer].playCard(mainCard, highestTrump)

            # Put the played card in the trick
            self.tricks[n][currentPlayer] = playedCard

        # Set a startingPlayer for the next trick
        trickWinner = self._getTrickWinner(n)
        self.startingPlayerForTrick[n if n == self.nTricks - 1 else n + 1] = trickWinner

        # Give the cards of the trick to whoever should get them
        self.giveBackCards(n, trickWinner)

        # Display a recap of the trick to the human-player
        printh(f"End of trick {n + 1}, {self.players[trickWinner].name} won the trick.")

    def _getCalledPlayer(self) -> int:
        """Get the calledPlayer based on when the calledCard was played"""

        # If this game doesn't have a calledCard
        if self.calledCard is None:
            return None

        # If card in the _dog, the taker has called himself as such, there is no calledPlayer
        if self.calledCard in self._dog:
            return None

        # Get the player associated to the called card
        for trick in self.tricks:
            for card in trick:
                if card == self.calledCard:
                    calledPlayer = trick.index(card)
                    # If the player who played the calledCard is the taker, the taker has called himself as such, there
                    # is no calledPlayer
                    if calledPlayer == self.players.index(self.players[self.playerTaking]):
                        return None
                    # Otherwise, the player who played the card is the calledPlayer
                    else:
                        return calledPlayer

    # @profile
    def _getTrickWinner(self, n: int) -> int:
        """Find which player has played the card that won the trick."""

        # If it was already calculated, return the cached value
        if n in self._trickWinners:
            return self._trickWinners[n]

        # Get the current trick from the trick history
        trick: List[str] = self.tricks[n]

        # Get the mainCard for the trick
        # The mainCard is the first card played, except if the excuse has been played where the mainCard becomes the
        # second card played
        if trick[self.startingPlayerForTrick[n]] == 'EX':
            startingPlayerIndex = self.startingPlayerForTrick[n] - 1
            mainCard = trick[startingPlayerIndex]
        else:
            mainCard = trick[self.startingPlayerForTrick[n]]
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

        # If the excuse is played in the last trick
        if self.nTricks - 1 == n and 'EX' in trick and self.chelemPlayer is not None:
            # If the same team won all tricks before the last, if that team also played the excuse in the last trick:
            if self.teamWonAllTricks(range(self.nTricks - 1)[0]):
                # The excuse is in the only situation in which it wins
                winningCard = 'EX'

        # Get the winner by looking up the index of the winningCard
        trickWinner = trick.index(winningCard)

        # Save to cache the player that won the trick
        self._trickWinners[n] = trickWinner

        # Return the winner
        return trickWinner

    # @profile
    def teamWonAllTricks(self, tricks: range) -> (bool, str):
        """Get a boolean value saying if all tricks were won by the same team, and a string telling you which team
        won."""

        # List of the players that are in the taker's team
        takerTeam = [self.playerTaking, self.calledPlayer]

        # Find out if one team won all the tricks of the game
        allTricksWonByOneTeam = all([self._getTrickWinner(n) in takerTeam for n in range(tricks)])
        # If this isn't the case, return False
        if not allTricksWonByOneTeam:
            return False, None

        # Return the winning team by looking at an arbitrary trick which must have been won by the team that won all tricks
        if self._getTrickWinner(0) in takerTeam:
            return True, 'taker'
        elif self._getTrickWinner(0) not in takerTeam:
            return True, 'defense'

    def giveBackCards(self, n: int, trickWinner: int) -> None:
        """Give the cards to the winner, and handle situations in which the cards go to other players"""

        # Get all the cards that were played in the trick
        trick = self.tricks[n].copy()

        # Return the excuse to its initial owner if the excuse has been played in this trick and if this isn't the last
        # trick
        if 'EX' in trick and self.nTricks - 1 != n:
            # Get the identity of the player that played the excuse in the Game.players list
            self.playedExcuse = trick.index('EX')
            # If the player who played the excuse is not already getting back his card (so that he doesn't ow himself a
            # card)
            if self.playedExcuse != trickWinner:  # Happens if this is the last card of a player in a Chelem
                # Give back the card
                self.players[self.playedExcuse].giveCardsWon([trick.pop(self.playedExcuse)])
                # Memorize whom the person that played the excuse ows a card
                self.recipientOfOwedExcuseCard = trickWinner

        # After the excuse has been given to the right person, the rest of the trick goes to its winner
        self.players[trickWinner].giveCardsWon(trick)

        # The player who played the excuse ows a 1/2 point card to the player that won the trick in which the excuse
        # was played.
        # If there is a player to whom a card is owed
        if self.recipientOfOwedExcuseCard is not None:
            self.giveOwedExcuseCard(self.playedExcuse)

        # If this isn't the last trick end function here
        if n != self.nTricks - 1:
            return

        # Get the player that played the calledCard, is None if the card wasn't played
        self.calledPlayer = self._getCalledPlayer()

        # If this is the last trick and the card is still owed, check if any teammate of the person that owes the card
        # has a card to give to the recipient
        if self.recipientOfOwedExcuseCard is not None:
            # In a 5-player game, try with the calledPlayer
            if self.calledPlayer is not None and self.playedExcuse == self.playerTaking:
                self.giveOwedExcuseCard(self.calledPlayer)
            # In a 5-player game, try with the playerTaking
            elif self.calledPlayer is not None and self.playedExcuse == self.calledPlayer:
                self.giveOwedExcuseCard(self.playerTaking)
            # In any game, another defendant might have a card
            else:
                # For each player
                for i in range(self.playerCount):
                    # Find a player that is not the taker or the person they might have called
                    if i != self.playerTaking and i != self.calledPlayer:
                        self.giveOwedExcuseCard(i)
                    # If this defender was able to provide a card, don't also make another player give a card
                    if self.recipientOfOwedExcuseCard is None:
                        break

        # If the contract was a guard against the dog, give the cards that were in the dog to one of the defendants
        if self.guardAgainstCards is not None:
            # For each player
            for i in range(self.playerCount):
                # Find a player that is not the taker or the person they might have called
                if i != self.playerTaking and i != self.calledPlayer:
                    self.players[i].giveCardsWon(self.guardAgainstCards)
                    # If this defender was able to provide a card, don't also make another player give a card
                    break

    def giveOwedExcuseCard(self, owedCardHolder) -> None:
        """The person passed as parameter gives a card to the player that won the trick in which the excuse was played
        """

        # Get all the cards of the person that ows a card, that have a value of 1/2 point
        halfAPointCards = [card for card in self.players[owedCardHolder].cardsWon
                           if 'EX' not in card and '1T' not in card and '21T' not in card and
                           ('T' in card or Game.cardNameToValue[card[:-1]] <= 10)]
        # If there is a card that can be given
        if len(halfAPointCards) > 0:
            # Give that card from the players own stack and put it into the other players stack
            owedCardHolderCardsWon = self.players[owedCardHolder].cardsWon
            owedCard = owedCardHolderCardsWon.pop(owedCardHolderCardsWon.index(halfAPointCards[0]))
            self.players[self.recipientOfOwedExcuseCard].giveCardsWon([owedCard])
            # No card is owed anymore
            self.recipientOfOwedExcuseCard = None

    def cardToPoints(self, card) -> float:
        if card[-1] in Game.suits:
            cardValue = Game.cardNameToValue[card[:-1]]
            if cardValue < 10:
                return 0.5
            else:
                # Example: 'J'.value = 11 => 11 - 10 + 0.5 = 1.5
                return cardValue - 10 + 0.5
        elif 'T' in card and card not in ['1T', '21T']:
            return 0.5
        else:
            return 4.5

    # @profile
    def countPoints(self):

        # Get the points every player made during the game
        for i in range(self.playerCount):
            self.wonCardPoints[i] = sum([self.cardToPoints(card) for card in self.players[i].cardsWon])

        # Get the points of the taker
        takerPoints = self.wonCardPoints[self.playerTaking]
        # Get the number of oudlers hold by the taker
        takerOudlers = [card for card in self.players[self.playerTaking].cardsWon
                        if card in ['1T', '21T', 'EX']]

        # In a 5-player game
        if self.calledPlayer is not None:
            # Merge the taker's cardPoints and the ones of his partner
            takerPoints += self.wonCardPoints[self.calledPlayer]
            # Merge the taker's oudlerCount and the one of his partner
            takerOudlers.extend([card for card in self.players[self.calledPlayer].cardsWon
                                 if card in ['1T', '21T', 'EX']])

        # In a 3 or 5 player game the points are rounded up for the winning team and rounded down for the loosing one
        if self.playerCount == 3 or self.playerCount == 5:
            if takerPoints - Game.winConditionPoints[len(takerOudlers)] >= 0:
                math.ceil(takerPoints)
            else:
                math.floor(takerPoints)

        # The taker's points = the cardPoints - the required amount (linked to the amount of oudlers) + 25
        finalPoints = takerPoints - Game.winConditionPoints[len(takerOudlers)] + 25

        # This value is multiplied by the contract
        currentContractMultiplier = Game.contractMultiplier[self.highestContract]
        finalPoints = finalPoints * currentContractMultiplier

        # Determine if the taker has won or lost
        if finalPoints > 0:
            takerWon = True
        else:
            takerWon = False

        # Check if one team won all tricks
        allTricksWon, allTricksWinner = self.teamWonAllTricks(self.nTricks)

        # Get last trick (trick before last in case of a Chelem)
        if allTricksWon:
            petitAuBoutTrick = self.tricks[self.nTricks - 2]
        else:
            petitAuBoutTrick = self.tricks[self.nTricks - 1]
        # Check if the petit was played in that trick
        if petitAuBoutTrick.count('1T') == 1:
            # Petit au bout, adds or removes points depending on who played it
            if self._getTrickWinner(self.nTricks - 1) in [self.playerTaking, self.calledPlayer]:
                # If the taker or the called player played the petit, add 10 points, multiplied by the contract's
                # multiplier
                finalPoints += 10 * currentContractMultiplier
            else:
                # If the defense played the petit, remove 10 points, multiplied by the contract's multiplier
                finalPoints -= 10 * currentContractMultiplier

        # Get points for announced handfuls if possible
        handfulValue = 0
        for handful in self.handfuls:
            if handful is not None:
                handfulValue += Game.handfulValues[handful]
        # Add to finalPoints if the taker won
        if takerWon:
            finalPoints += handfulValue
        # Remove from finalPoints if the taker lost
        else:
            finalPoints -= handfulValue

        # In case a Chelem has been made
        if allTricksWon:
            # If it was announced by the taker (can only be announced by the taker)
            if self.chelemPlayer is not None:
                finalPoints += 400 * currentContractMultiplier
            # If it wasn't announced, but the taker made a Chelem
            elif allTricksWinner == 'taker':
                finalPoints += 200 * currentContractMultiplier
            # If it wasn't announced, but the defense made a Chelem
            elif allTricksWinner == 'defense':
                # Every defendant gets 200 points
                for i in range(self.playerCount):
                    if i not in [self.playerTaking, self.calledPlayer]:
                        self.matchPoints[i] += 200  # no multiplicator
        # In case a Chelem has been failed (can only be announced by the taker)
        elif self.chelemPlayer is not None:
            finalPoints -= 200 * currentContractMultiplier

        # If the excuse is in the defense's hand, it is only worth 4 points
        if takerOudlers.count('EX') == 0 and allTricksWinner == 'defense':
            finalPoints += 0.5 * currentContractMultiplier

        # Give points to players, in a way in which their points all equal to zero
        # (ignoring the already given bonus for a Chelem)
        for i in range(self.playerCount):
            # In a 3-player game
            if self.playerCount == 3:
                if i == self.playerTaking:
                    # The player taking gets double the points
                    self.matchPoints[i] += finalPoints * 2
                else:
                    # The defendants each get the points
                    self.matchPoints[i] -= finalPoints
            # In a 4-player game
            elif self.playerCount == 4:
                # The player taking gets triple the points
                if i == self.playerTaking:
                    self.matchPoints[i] += finalPoints * 3
                else:
                    # The defendants each get the points
                    self.matchPoints[i] -= finalPoints
            # In a 5-player game
            elif self.playerCount == 5:
                # If a player was called
                if self.calledPlayer is not None:
                    # The player taking gets quadruple the points
                    if i == self.playerTaking:
                        self.matchPoints[i] += finalPoints * 4
                    # The defendants each get the points
                    else:
                        self.matchPoints[i] -= finalPoints
                # If no player was called
                else:
                    # The player taking gets double the points
                    if i == self.playerTaking:
                        self.matchPoints[i] += finalPoints * 2
                    # The called player gets his points
                    elif i == self.calledPlayer:
                        self.matchPoints[i] += finalPoints
                    # The defendants each get the points
                    else:
                        self.matchPoints[i] -= finalPoints

    def end(self) -> tuple:
        """Returns all information that is needed to start a new game with the already existing deck and players"""

        # Get a new deck
        deck = []
        for n in range(self.playerCount):
            deck.extend([cards for cards in self.players[n].cardsWon])

        # Set the players back to start
        for player in self.players:
            player.restart()

        return self.players, deck, self.matchPoints, self.dealer


class Player:
    def __init__(self, name: str, strategy: str):
        """An object holding data about a player and simulating a player's actions"""

        # VALIDATE PARAMETERS
        # A name to easily identify the players or the order in which they sit in
        self.name = str(name)

        validStrategies = ['human', 'random']
        if strategy in validStrategies:  # TODO: (LONG TERM) MORE STRATEGIES (AI) | pass question and options (and brain) to ai-function
            self.strategy = strategy
        else:
            raise PlayerException("Please use one of the following strategies:", validStrategies)

        # INITIALIZE VARIABLES
        self.hand = []

        self.cardsWon = []

        self.game: Game = None

    def rename(self, name) -> None:
        """Change the name of a player"""

        self.name = str(name)

    def joinGame(self, gameObject: Game):
        """Link a Game object to the player"""

        self.game = gameObject

    # @profile
    def _getDecision(self, question: str, options: List[str]) -> str:
        """Given an answer and set of possible options, a player has to decide which option to choose."""

        # Validate the format of the possible options
        if any([type(element) is not str for element in options]) or len(options) == 0:
            raise PlayerException("Parameter 'options' in 'decide' only takes a list of strings")

        # Show the question to the user if the user is a human player and return the option chosen by the player
        if self.strategy == 'human':
            printh(f"Hand: {sorted(self.hand, key=self._handSortKey)}", recipient=self.name)
            printh(question, recipient=self.name)

            # Get the player's decision
            playerAnswer = None
            while playerAnswer not in options:
                printh(f"Please enter one of the following options {options}:", recipient=self.name)
                if len(options) > 1:
                    playerAnswer = inputh()
                # While human-playing if there is only one option, choose it automatically
                else:
                    playerAnswer = options[0]

            return playerAnswer

        # Return a randomly chosen option
        elif self.strategy == 'random':
            printh(f"Hand: {sorted(self.hand, key=self._handSortKey)}", recipient=self.name)
            printh(question, recipient=self.name)
            printh(f"Please enter one of the following options {options}:", recipient=self.name)
            choice = rd.choices(options, k=1)[0]  # faster than rd.choice(l)
            printh(choice, recipient=self.name)
            return choice

    def addCardsToHand(self, cards: list, sort=True) -> None:
        """Add cards to a player's hand"""

        self.hand.extend(cards)
        if sort:
            self.sortHand()

    # @profile
    def sortHand(self) -> None:
        """Sorts the player's hand in the order of the deck's creation"""

        self.hand.sort(key=self._handSortKey)

    def _handSortKey(self, s: str) -> str:
        """Allows sorting of the cards in the same order as they were dealt"""

        return self.game.create_deck().index(s)

    def clearHand(self) -> [str]:
        """Empties a player's hand and returns the cards that were in it"""

        oldHand, self.hand = self.hand.copy(), []
        return oldHand

    def giveCardsWon(self, cards: list):
        """Transfers the cards into the stack of cards won by the player"""

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

        # Sort options in deck order
        options.sort(key=self._handSortKey)

        # Get decision from player
        card = self._getDecision(question, options)

        # If a player decides to put a trump into his aside, he has to show it to the other players
        if 'T' in card:
            self.game.showCards(self.game.players.index(self), [card])

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
        options.extend([card for card in self.game.create_deck() if 'K' in card])

        #  - If a player has all Kings, he can call a Queen. The same goes for the Queen, the Cavalryman and the Jack
        i = 0
        value = ['K', 'Q', 'C', 'J']
        while len([card for card in self.hand if value[i] in card]) == 4 and i < 4:
            options.extend([card for card in self.hand if value[i] in card])
            i += 1

        # Sort options in deck order
        options.sort(key=self._handSortKey)

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
        options = []

        # Eliminate the options that aren't possible
        if len(trumpsInHand) < trumpsNeededForHandful[0]:
            return None
        if len(trumpsInHand) >= trumpsNeededForHandful[0]:
            options.append('Simple handful')
        if len(trumpsInHand) >= trumpsNeededForHandful[1]:
            options.append('Double handful')
        if len(trumpsInHand) >= trumpsNeededForHandful[2]:
            options.append('Triple Handful')

        # Add the possibility not to call the handful
        options.append('Don\'t call handful')

        # Get decision from player
        decision = self._getDecision(question, options)

        # If the player decides not to call, the handful returns the same as if it wasn't possible
        if decision == 'Don\'t call handful':
            return None

        # Remove excuse from the cards to show if there are too many cards to show compared to the number needed for the
        # announced handful
        trumpsToShow = trumpsInHand.copy()
        trumpsNeeded = trumpsNeededForHandful[options.index(decision)]
        if 'EX' in trumpsToShow and len(trumpsToShow) > trumpsNeeded:
            trumpsToShow.remove('EX')
        # If the player still has more trumps than needed for his contract, ask which ones he doesn't want to show
        question = "Which card do you prefer not to reveal?"
        while len(trumpsToShow) > trumpsNeeded:
            options = trumpsToShow
            cardToRemove = self._getDecision(question, options)
            trumpsToShow.remove(cardToRemove)

        # Show the cards you have in a handful, starting from the lowest value one, until you showed all necessary ones,
        # including at last if available the excuse
        trumpsToShowSorted = sorted(trumpsToShow, key=self._handSortKey)
        self.game.showCards(self.game.players.index(self), trumpsToShowSorted)

        return decision

    # @profile
    def playCard(self, mainCard: str, highestTrump: int):
        """Make the player choose one of the cards in his hand to play in the trick"""

        # Define the question
        question = "Which card do you want to play in this trick?"

        # Base options are all the cards in the player's hand
        options = self.hand.copy()

        # If in a 5-player game, it is the first card of the first trick, remove any option of the same suit as the
        # calledCard except for the calledCard itself
        if self.game.calledCard is not None and self.game.tricks[0][0] == '':
            options = [card for card in options
                       if not (card[-1] == self.game.calledCard[-1] and not card == self.game.calledCard)]

        # If the first card of the trick has already been played, limit the options the player has according to
        # this card
        if mainCard is not None:
            mainCardValue, mainCardType = mainCard[:-1], mainCard[-1]

            # If the mainCard is part of a suit
            if mainCardType in Game.suits:
                # Check if the player has a card of the required suit in his hand
                cardsOfMainCardSuitInHand = [option for option in options if mainCardType in option]
                # If this is the case, all cards of the same suit can be played, and no other card
                if len(cardsOfMainCardSuitInHand) > 0:
                    options = cardsOfMainCardSuitInHand
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
                                                    and int(option[:-1]) > highestTrump]
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
        if 'EX' in self.hand and 'EX' not in options:
            options.append('EX')

        # Get the card the player plays
        card = self._getDecision(question, options)
        self.hand.remove(card)
        return card

    def restart(self):
        self.hand = []
        self.cardsWon = []


if __name__ == '__main__':

    games = 0
    tests = 1e4
    while games < tests:
        game = Game(rd.randint(3, 5), lastDealer=rd.randint(0, 3))
        game.play()
        games += 1
