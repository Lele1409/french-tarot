import time


class TarotGameProxy(object):
	def __init__(self, created_at=time.time()):
		self.created_at: float = created_at
		self.players: [tuple] = []

		self.game = None  # TODO: link to actual game object

	def add_player(self, player: str):
		self.players.append((time.time, player))
