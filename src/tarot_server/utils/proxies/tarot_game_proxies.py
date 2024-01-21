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
						"is_replaced": False,
						# Indicates that the other players have been informed
						# about this player getting replaced
						"replace_reported": False
					})

	def set_disconnected(self) -> None:
		self["is_connected"] = False
		self["disconnected_at"] = time.time()

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

		self._game = None  # TODO: link to actual game object (created on start)
		self.game_running = False
		self.game_finished = False

	def add_player(self, player: str) -> None:
		self._players.update({player: TarotPlayerProxy()})

	def get_players(self) -> dict[str, TarotPlayerProxy]:
		return self._players

	def get_player(self, player: str) -> TarotPlayerProxy:
		return self._players.get(player)

	def get_player_id(self, player: TarotPlayerProxy) -> str:
		return [k for k, v in self._players.items() if v == player][0]

	def is_accepting_more_players(self) -> bool:
		if self._invite_only:
			# TODO: add possibility of invite-only mode
			return False
		# If no more players are accepted into the lobby
		if len(self._players) >= 5 or self.game_running:
			return False
		return True

# TODO: disconnected players:
# 	- connected players should be informed about the other player's
# 	  disconnect after [10]s
# 	- the disconnected player should have [90]s to reconnect
#	  before getting replaced by an automated player
#		HOW DO WE CHECK THIS?
#
