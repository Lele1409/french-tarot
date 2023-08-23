from secrets import token_hex


class Match:
    def __init__(self):
        self.match_id: str = None
        self.players: list[Player] = []

    def genMatchID(self):
        self.match_id = token_hex(16)

    def addPlayer(self):
        ...

    def createDeck :
        ...

