import secrets
import time

import flask_socketio
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user
from flask_socketio import Namespace, disconnect, join_room, leave_room  # NOQA
from flask_user import login_required

from src.config.configLoader import config_tarot_server as config
from src.tarot_server.server import socketio
from src.tarot_server.utils.tarot_game_proxies import TarotGameProxy, \
	TarotPlayerProxy

views_lobby = Blueprint('lobby', 'tarot_server', url_prefix='/lobby')


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
		if self.get(code) is not None:
			return True
		else:
			return False

	def is_joignable(self, user: str, code: str) -> bool:
		# First check if the lobby's status has been changed
		# to non-joignable
		room = self[code]
		if not room.is_accepting_more_players():
			# Get the room the user was last in
			past_room_code: str = self.get_room_code(user)
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

	def get_room_code(self, player: str) -> str:
		return self._players.get(player)


tarot_rooms: TarotRooms[TarotGameProxy] = TarotRooms()


@views_lobby.route('/')
@login_required
def create():
	code_len = int(config['Lobby.Security']['code_length']) // 2
	code = secrets.token_hex(code_len).upper()
	while tarot_rooms.room_exists(code):
		code = secrets.token_hex(code_len).upper()
	tarot_rooms.create(code)
	return redirect(url_for('lobby.join', lobby_code=code))


@views_lobby.route('/<string:lobby_code>')
@login_required
def join(lobby_code=None):
	if not tarot_rooms.room_exists(lobby_code):
		# TODO: display some sort of information to the user
		#  that the lobby does not exist before sending them
		#  back to the menu
		return redirect(url_for('menu.menu'))
	if not tarot_rooms.is_joignable(current_user.id, lobby_code):
		# TODO: display some sort of information to the user
		#  about why the wasn't able to join, and/or redirect
		#  him to an observer page
		return redirect(url_for('menu.menu'))
	return render_template('lobby.html', code=lobby_code)


# TODO: Handle socket.io errors

class LobbyNamespace(Namespace):
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
		if not (endpoint == 'lobby' and tarot_rooms.room_exists(lobby_code)):
			disconnect()

		player = current_user.id

		# Remove the player from the last socket room he was in
		# (only if he was previously connected to one)
		last_room = tarot_rooms.get_room_code(player)
		if last_room is not None:
			leave_room(last_room)

		# Join the tarot room
		tarot_rooms.join(
			user=player,
			code=lobby_code
		)

		# Finally, join the player to the new socket room
		join_room(lobby_code)

	def on_disconnect(self):  # NOQA
		room = tarot_rooms[tarot_rooms.get_room_code(current_user.id)]
		# If the player was in a room during disconnect
		if room is not None:
			player: TarotPlayerProxy = room.get_player(current_user.id)
			player.set_disconnected()

	def on_manual_debug(self, data):  # NOQA
		print("REF:", request.referrer, "DATA:", data)
		print(flask_socketio.rooms())


def run_background_update():
	last_execution = time.time()
	while True:
		time_since_last = time.time() - last_execution
		if time_since_last > 2:
			last_execution = time.time()
			lobby_background_update()
		else:
			socketio.sleep(2 - time_since_last)


def lobby_background_update():
	...


socketio.start_background_task(target=run_background_update)
socketio.on_namespace(LobbyNamespace('/lobby'))
