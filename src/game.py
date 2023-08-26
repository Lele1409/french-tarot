class Game:
    def __init__(self):
        self.players: list[Player] = []
        self.deck: list[Card] = []
        self.dog: list[Card] = []
        self.aside: list[Card] = []
        self.current_player: str = starting_player
        self.tricks: list[Trick] = []
        self.contract_type: str = None
        self.taking_player: str = None
        self.called_player: str = None
        self.chelem_player: str = None
        self.defence: list[Player] = []
        self.attack: list[Player] = []
        self.handful_players: list[Player] = []
        self.called_king: str = None
        self.first_trick: bool = True
        self.discard_pile: list[Card] = []


    def dealCards(self, deck, players, current_player):
        ... # TODO: deal cards


    def chooseContract(self, current_player)
        """choose contract and put taking player in adequate categories"""

        contract_options = {"Pass": 0, "Small": 1, "Guard": 2, "Guard Without": 3, "Guard Against": 4}  # contract hierarchy: Pass < Small < Guard < Guard Without < Guard Against
        for Player in players :

            contrat=getDecision(Player.type,contract,contract_options)

        self.contract_type =
        if contract_type == "Pass":
            endGame()
        self.taking_player =
        self.attack.append(self.taking_player)
        self.chelem_player =

    def callPlayer(self, taking_player):
        '''call King if there are 5 players'''

        nbPlayers = len(players)
        if nbPlayers == 5:
            ...
            self.called_player =
            self.called_king =

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