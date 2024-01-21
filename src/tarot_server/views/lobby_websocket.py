import flask_socketio
from flask import request
from flask_login import current_user
from flask_socketio import Namespace, disconnect, join_room, leave_room  # NOQA

from src.tarot_server.utils.proxies.tarot_game_proxies import TarotPlayerProxy


# TODO: Handle socket.io errors

class LobbyNamespace(Namespace):
	def set_tarot_rooms(self, tarot_rooms):
		self.tarot_rooms = tarot_rooms

	def trigger_event(self, event, sid, *args):
		if args:
			super().trigger_event(event, sid, *args)
		else:
			super().trigger_event(event, sid)
	# TODO: check for long disconnects

	def on_connect(self):  # NOQA
		# Get the referrer header the client tried to connect with
		referrer: str = request.referrer

		# Try to get the endpoint of the request, and if it exists,
		# get the lobby_code to find out to which lobby the user
		# tries to connect to.
		try:
			endpoint: str = referrer.split('/')[3]
			lobby_code: str = referrer.split('/')[4]
		except KeyError:
			disconnect()
			return

		# If the request is not coming from the '/lobby' page
		# or the client tries to connect to a room that does not exist anymore
		if not (endpoint == 'lobby' and self.tarot_rooms.room_exists(lobby_code)):
			disconnect()

		player = current_user.id

		# Remove the player from the last socket room he was in
		# (only if he was previously connected to one)
		last_room = self.tarot_rooms.get_room_code_by_player(player)
		if last_room is not None:
			leave_room(last_room)

		# Join the tarot room
		self.tarot_rooms.join(
			user=player,
			code=lobby_code
		)

		# Finally, join the player to the new socket room
		join_room(lobby_code)

	def on_disconnect(self):  # NOQA
		room = self.tarot_rooms[
			self.tarot_rooms.get_room_code_by_player(current_user.id)]
		# If the player was in a room during disconnect
		if room is not None:
			player: TarotPlayerProxy = room.get_player(current_user.id)
			player.set_disconnected()

	def on_manual_debug(self, data):  # NOQA
		print("REF:", request.referrer, "DATA:", data)
		print(flask_socketio.rooms())
