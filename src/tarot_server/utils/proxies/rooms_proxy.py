from src.tarot_server.utils.proxies.tarot_game_proxies import TarotGameProxy, \
	TarotPlayerProxy


class TarotRooms(dict):
	def __init__(self) -> None:
		super().__init__()
		self.setdefault(None)

		# Add a dictionary to easily find to which
		# game a player has been connected to last
		self._players: dict = {}
		self._players.setdefault(None)

	def room_exists(self, code: str) -> bool:
		"""Checks if there is a room object associated with
		 the supplied code"""
		if self.get(code) is None:
			return False
		else:
			return True

	def is_joignable(self, user: str, code: str) -> bool:
		# First check if the lobby's status has been changed
		# to non-joignable
		room = self[code]
		if not room.is_accepting_more_players():
			# Get the room the user was last in
			past_room_code: str = self.get_room_code_by_player(user)
			# If the client is trying to reconnect to a lobby,
			# he has disconnected from
			if past_room_code == code:
				past_room: TarotGameProxy = self[past_room_code]
				player: TarotPlayerProxy = past_room.get_player(user)
				# If the client is trying to reconnect to a game,
				# he hasn't yet been replaced in
				if not player['is_replaced']:
					# User disconnected not to long ago
					return True
			# User has either joined to late,
			# or got replaced while reconnecting
			return False
		# Anyone can join
		return True

	def create(self, code: str) -> None:
		self.update({code: TarotGameProxy()})

	def join(self, user: str, code: str) -> None:
		self._players.update({user: code})
		self.get(code).add_player(user)

	def remove(self, code: str) -> None:
		self.pop(code)

	def get_room_by_player(self, player: str) -> TarotGameProxy:
		return self[self.get_room_code_by_player(player)]

	def get_room_code_by_player(self, player: str) -> str:
		return self._players.get(player)

	def get_room_code_by_room(self, room: TarotGameProxy) -> str:
		return [k for k, v in self.items() if v == room][0]
