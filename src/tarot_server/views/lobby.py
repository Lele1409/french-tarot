import secrets

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user
from flask_socketio import disconnect
from flask_user import login_required

from src.config.configLoader import config_tarot_server as config
from src.tarot_server.server import socketio
from src.tarot_server.utils.tarot_game_proxy import TarotGameProxy

views_lobby = Blueprint('lobby', 'tarot_server', url_prefix='/lobby')


class TarotRooms(dict):
	def __init__(self):
		super().__init__()
		self.setdefault(None)

	def room_exists(self, code):
		"""Checks if there is a room object associated with
		 the supplied code"""
		if self.get(code) is not None:
			return True
		else:
			return False

	def create(self, code):
		print(f"Created lobby {code}")
		self.update(
			{code: TarotGameProxy()})

	def join(self, user, code):
		print(f"Player {user} joined lobby {code}")
		self.get(code).add_player(user)

	def remove(self, code):
		self.pop(code)


# TODO: if all users left a lobby, close the lobby


tarot_rooms = TarotRooms()


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
	return render_template('lobby.html', code=lobby_code)


# TODO: Handle socket.io errors


@socketio.on('connect', namespace='/lobby')
def on_connect():
	print(current_user.id, ' connected')
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

	if endpoint == 'lobby' and tarot_rooms.room_exists(lobby_code):
		tarot_rooms.join(
			user=current_user.id,
			code=lobby_code
		)
	else:
		disconnect()


@socketio.on('disconnect', namespace='/lobby')
def on_disconnect():
	print(current_user.id, ' disconnected')


@socketio.on('MANUAL_DEBUG', namespace='/lobby')
def on_manual_debug(data):
	print("REF:", request.url, request.root_url, request.host_url, request.base_url, "DATA:", data)
