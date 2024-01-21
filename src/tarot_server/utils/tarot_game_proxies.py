import time


class TarotPlayerProxy(dict):
	def __init__(self):
		super().__init__()
		self.setdefault(None)
		self.update({
						"is_connected"   : True,
						"disconnected_at": None,
						"is_replaced": False
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
	def __init__(self, created_at=time.time()) -> None:
		self._created_at: float = created_at
		self._players: dict = {}

		self._invite_only = False

		self._game = None  # TODO: link to actual game object (created on start)
		self.game_running = False

	def add_player(self, player: str) -> None:
		self._players.update({player: TarotPlayerProxy()})

	def get_player(self, player: str) -> TarotPlayerProxy:
		return self._players.get(player)

	def is_accepting_more_players(self) -> bool:
		if self._invite_only:
			# TODO: add possibility of invite-only mode
			return False
		elif len(self._players) >= 5 or self.game_running:
			return False
		return True

# TODO: disconnected players:
# 	- connected players should be informed about the other player's
# 	  disconnect after [10]s
# 	- the disconnected player should have [90]s to reconnect
#	  before getting replaced by an automated player
#		HOW DO WE CHECK THIS?
#
