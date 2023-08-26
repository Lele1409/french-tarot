from src.tarot.player import Player
from secrets import token_hex


class Match:
    def __init__(self):
        self.match_id: str = None
        self.players: list[Player] = []

        # Example
        # for _ in range(nb_of_hands_to_play):
        #     game_hand = Game([Player], deck, Player)
        #     game_hand.start_game_hand()
        #     deck = game_hand.get_results()

    def genMatchID(self):
        self.match_id = token_hex(16)

    def addPlayer(self):
        ...

    def createDeck :
        ...

