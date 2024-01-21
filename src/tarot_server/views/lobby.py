import secrets

from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user
from flask_user import login_required

from src.config.configLoader import config_tarot_server as config
from src.tarot_server.server import socketio
from src.tarot_server.utils.background_runner import run_background_update
from src.tarot_server.utils.proxies.room_proxy import TarotRooms
from src.tarot_server.utils.proxies.tarot_game_proxies import TarotGameProxy, \
	TarotPlayerProxy
from src.tarot_server.views.lobby_websocket import LobbyNamespace

views_lobby = Blueprint('lobby', 'tarot_server', url_prefix='/lobby')

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


def lobby_background_update():
	room: TarotGameProxy
	for room in tarot_rooms:
		if room is None:
			continue

		player: TarotPlayerProxy
		for player in room.get_players():
			# Inform other players about a players disconnect
			socketio.emit("info_player_disconnect",
						  player,
						  to=tarot_rooms.get_room_code_by_room(room))

			# Replace player disconnected for too long

		# Close lobbies where all players are replaced
		# or if the game has finished
		players = room.get_players()


socketio.start_background_task(target=run_background_update,
							   func=lobby_background_update,
							   interval=2)

lobby_namespace = LobbyNamespace('/lobby')
lobby_namespace.set_tarot_rooms(tarot_rooms)
socketio.on_namespace(lobby_namespace)
