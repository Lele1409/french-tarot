from src.decision.decision import getDecision
from src.tarot.player import Player

DOG_SIZES = {3: 6, 4: 6, 5: 3}



class Game:
    def __init__(self, players=[Player], deck=[str], starting_player=Player):
        self.players: list[Player] = players
        self.deck: list[str] = deck
        self.dog: list[Card] = []
        self.aside: list[Card] = []
        self.current_player: str = starting_player  # TODO: put into match?
        self.tricks: list[Trick] = []
        self.contract_type: str = "Pass"
        self.taking_player: Player = None
        self.called_player: Player = None
        self.chelem_player: Player = None
        self.defence: list[Player] = []
        self.attack: list[Player] = []
        self.handful_players: list[Player] = []
        self.called_king: str = None
        self.first_trick: bool = True
        self.discard_pile: list[Card] = []


    def dealCards(self, deck, players, current_player):
        """
        there are 78 cards in the deck

        for a game of 5 players:
            - you deal 15 cards/player
            - the dog is composed of 3 cards
            - there are 24 opportunities to put a card in the dog
            - at each opportunity, you have 1/8 chances to put a card in the dog
            - minimum amount of cards to have to distribute before putting a card in the dog at every opportunity = number of cards missing from dog x4
            - nombre de carte minimum a avoir a distribuer avant de mettre une carte dans le chien a chaque opportunite = nb de carte restante a mettre dans le chien x4
            - if there is 0 card in the dog and 12 cards left to deal, a card must be put in the dog at every opportunity
            - if there is 1 card in the dog and 8 cards left to deal, a card must be put in the dog at every opportunity
            - if there are 2 cards in the dog and 4 cards left to deal, a card must be put in the dog at every opportunity

        for a game of 4 players:
            - you deal 18 cards/player
            - the dog is composed of 6 cards
            - there are 23 opportunities to put a card in the dog
            - if there is 0 card in the dog and 24 cards left to deal, a card must be put in the dog at every opportunity
            - if there is 1 card in the dog and 20 cards left to deal, a card must be put in the dog at every opportunity
            - if there are 2 cards in the dog and 16 cards left to deal, a card must be put in the dog at every opportunity
            - if there are 3 cards in the dog and 12 cards left to deal, a card must be put in the dog at every opportunity
            - if there are 4 cards in the dog and 8 cards left to deal, a card must be put in the dog at every opportunity
            - if there are 5 cards in the dog and 4 cards left to deal, a card must be put in the dog at every opportunity

        for a game of 3 players:
            - you deal 24 cards/player
            - the dog is composed of 6 cards
            -- there are 23 opportunities to put a card in the dog
            - if there is 0 card in the dog and 24 cards left to deal, a card must be put in the dog at every opportunity
            - if there is 1 card in the dog and 20 cards left to deal, a card must be put in the dog at every opportunity
            - if there are 2 cards in the dog and 16 cards left to deal, a card must be put in the dog at every opportunity
            - if there are 3 cards in the dog and 12 cards left to deal, a card must be put in the dog at every opportunity
            - if there are 4 cards in the dog and 8 cards left to deal, a card must be put in the dog at every opportunity
            - if there are 5 cards in the dog and 4 cards left to deal, a card must be put in the dog at every opportunity
        """

        for # TODO: deal cards


    def chooseContract(self)
        """choose contract and put taking player in adequate categories"""

        contract_options: list[str] = ["Small", "Guard", "Guard Without", "Guard Against"]  # contract hierarchy: Pass < Small < Guard < Guard Without < Guard Against

        for player in self.players:  # TODO: verify player order
            contract_options.insert(0, "Pass")
            player_contract: str = getDecision(player, "contract", contract_options)
            if player_contract != "Pass":
                player_chelem: str = getDecision(player, "chelem", ["yes", "no"])
                if player_chelem == "yes":
                    self.chelem_player = player
                self.contract_type = player_contract
                self.taking_player = player
            for contract in contract_options:
                if contract_options.index(contract) < contract_options.index(player_contract):
                    contract_options.remove(contract)
        if self.contract_type == "Pass":
            endGame()
        self.attack.append(self.taking_player)

    def callPlayer(self):
        """call King if there are 5 players"""

        nbPlayers = len(self.players)
        if nbPlayers == 5:
            return None

        suits = ['♠', '♥', '♣', '♦']
        for rank in ['K', 'Q', 'C', 'J']:
            options = [rank + suit for suit in suits]
            for card in self.taking_player.hand:
                for option in options:
                    if option == card :
                        options.remove(option)
            if not options:
                options = [rank + suit for suit in suits]
                break

        self.called_king = getDecision(self.taking_player, "King", options)
        for player in self.players:
            for card in player.hand:
                if card == self.called_king :
                    self.called_player=player


    def createDog(self, deck):
        '''create dog with what remains of the deck'''

        self.dog = deck

    def takeDog(self, contract_type, taking_player):
        '''put the dog in the corect place depending on contract'''

        if contract_type == "Small" or contract_type == "Guard":
            ... # TODO : add dog to taking player hand
        elif contract_type == "Guard Without":
            self.aside = dog
        else:
            ... # TODO: add dog to defence

    def makeAside(self, contract_type, taking_player):
        '''let taking player make aside if contract allows it'''

        if contract_type == "Small" or contract_type == "Guard":
            ... # TODO: taking player chooses his aside
            self.aside=

    def playTricks(self, first_trick, current_player, called_king, ):
        '''play every trick of the game'''

        hand_size=len(Hand) # TODO: "Hand" doesn't exist yet
        for i in range (hand_size):
            if i == 0 :
                for Player in players :
                    ... # TODO: call handfuls
                    ... # TODO: play card without using called king's color
                    self.current_player=  # TODO: set current player to next player

            else :
                for Player in players:
                    ... # TODO: play card normally
                    self.current_player =  # TODO: set current player to next player
            # TODO: add trick to discard pile

    def endGame(self, discard_pile):
        '''prepare next game'''

        self.deck=discard_pile
        # TODO: calculate game score and add to match score
        # TODO: new game


# ObjectNames
# functionNames
# variable_names
# __private_variable