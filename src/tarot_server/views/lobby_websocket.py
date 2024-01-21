import flask_socketio
from flask import request, url_for
from flask_login import current_user
from flask_socketio import Namespace, disconnect, join_room, leave_room  # NOQA

from src.tarot_server.server import socketio
from src.tarot_server.utils.proxies.tarot_game_proxies import TarotGameProxy, \
	TarotPlayerProxy
from src.tarot_server.views.lobby import tarot_rooms


# TODO: Handle socket.io errors

class LobbyNamespace(Namespace):
	def on_connect(self):  # NOQA
		# Get the referrer header the client tried to connect with
		referrer: str = request.referrer

		# Try to get the endpoint of the request, and if it exists,
		# get the room_code to find out to which lobby the user
		# tries to connect to.
		try:
			endpoint: str = referrer.split('/')[3]
			room_code: str = referrer.split('/')[4]
		except KeyError:
			disconnect()
			return

		# If the request is not coming from the '/lobby' page
		# or the client tries to connect to a room that does not exist anymore
		if not endpoint == 'lobby' or not tarot_rooms.room_exists(room_code):
			disconnect()
			return

		player = current_user.id

		# Remove the player from the last socket room he was in
		# (only if he was previously connected to one)
		last_room = tarot_rooms.get_room_code_by_player(player)
		if last_room is not None:
			leave_room(last_room)

		# Join the tarot room
		self.tarot_rooms.join(
			user=player,
			code=room_code
		)

		# Finally, join the player to the new socket room
		join_room(room_code)

		# Inform the other player's about the player connecting
		update_client_player_list(room_code)

	def on_disconnect(self):
		room: TarotGameProxy = \
			tarot_rooms.get_room_by_player(current_user.id)
		# If the player was in a room during disconnect
		if room is not None:
			player: TarotPlayerProxy = room.get_player(current_user.id)
			player.set_disconnected()

	def on_action_player_force_quit(self):
		player = current_user.id
		room_code = tarot_rooms.get_room_code_by_player(player)
		room = tarot_rooms.get_room_by_player(player)

		room.remove_player(player)
		update_client_player_list(room_code)

	def on_action_game_start(self):
		print('Game started')

		room_code = self.tarot_rooms.get_room_code_by_player(current_user.id)

		# if conditions for game start are met
		socketio.emit('info_redirect',
					  url_for('lobby.game', lobby_code=room_code),
					  namespace='/lobby',
					  to=room_code)
		room = self.tarot_rooms[room_code]
		room.game_running = True

	def on_manual_debug(self, data):
		print("REF:", request.referrer, "DATA:", data)
		print("Rooms:", flask_socketio.rooms())
		print("Players in rooms", [self.tarot_rooms[room].get_players() for room in flask_socketio.rooms() if
								   len(room) == 8])
		print("Players:", [player for player in [room.get_players().values() for room in self.tarot_rooms.values() if room is not None]])


def update_client_player_list(room_code):
	socketio.emit('info_room_players',
				  tarot_rooms[room_code].get_players(),
				  namespace='/lobby',
				  to=room_code)
