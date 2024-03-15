import time


class TarotPlayerProxy(dict):
	def __init__(self):
		super().__init__()
		self.setdefault(None)
		self.update({
						# The status of the user
						"is_connected"   : True,
						# The time at which the user has been disconnected
						"disconnected_at": None,
						# Indicates that the other players have been informed
						# about the user's current disconnect
						"disconnect_reported": False,
						# Indicates that the user is an AI
						"is_ai": False,
						# Indicates that the other players have been informed
						# about this player getting replaced
						"replace_reported": False
					})

		# TODO: link to actual game object (created on start)
		#  means that all methods here need to run also on the
		#  non-proxy object
		self.player = None

	def set_disconnected(self) -> None:
		self["is_connected"] = False
		self["disconnected_at"] = time.time()

	def replace_by_ai(self):
		self['is_ai'] = True

	def get_time_since_last_seen(self) -> float:
		return time.time() - self["disconnected_at"]


# TODO: if all users left a lobby, close the lobby


class TarotGameProxy:
	# TODO: add a log of all server-side emitted data for reconnecting
	#  users to catch back up to the current point in time
	#  (also do this in the lobby, or send a current_state)
	def __init__(self, created_at=time.time()) -> None:
		self._created_at: float = created_at
		self._players: dict[str, TarotPlayerProxy] = {}

		self._invite_only = False

		# TODO: link to actual game object (created on start)
		#  means that all methods here need to run also on the
		#  non-proxy object
		self._game = None
		self.game_running = False
		self.game_can_be_deleted = False

	def add_player(self, player: str) -> None:
		self._players.update({player: TarotPlayerProxy()})

	def remove_player(self, player: str) -> None:
		self._players.pop(player)

	def get_players(self) -> dict[str, TarotPlayerProxy]:
		return self._players

	def get_player(self, player: str) -> TarotPlayerProxy:
		return self._players.get(player)

	def get_player_id_by_player(self, player: TarotPlayerProxy) -> str:
		return [k for k, v in self._players.items() if v == player][0]

	def is_accepting_more_players(self) -> bool:
		if self._invite_only:
			# TODO: add possibility for invite-only mode
			return False
		# If no more players are accepted into the lobby
		if len(self._players) >= 5 or self.game_running:
			return False
		return True
