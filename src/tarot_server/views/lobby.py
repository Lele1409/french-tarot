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
		#  about why he wasn't able to join, and/or redirect
		#  him to an observer page
		return redirect(url_for('menu.menu'))
	return render_template('lobby.html', code=lobby_code)


def lobby_background_update() -> None:
	room: TarotGameProxy
	for room in list(tarot_rooms.values()).copy():
		if room is None:
			continue
		else:
			check_players_status(room)
			check_empty_room(room)


def check_players_status(room: TarotGameProxy) -> None:
	player: TarotPlayerProxy
	# The for loop is executed on a copy of the list because otherwise
	# the dictionary might change during execution (deletion of parts of it)
	for player in list(room.get_players().values()).copy():
		if player['is_connected']:
			continue

		player_id = room.get_player_id(player)

		# Inform players about another player's disconnect
		if player.get_time_since_last_seen() > 10:  # TODO: configurability
			if not player['disconnect_reported']:
				player['disconnect_reported'] = True
				socketio.emit("info_player_disconnected",
							  player_id,
							  namespace='/lobby',
							  to=tarot_rooms.get_room_code_by_room(room))

		# Replace player disconnected for too long if the game is already running
		if player.get_time_since_last_seen() > 30:  # TODO: configurability
			if room.game_running:
				if not player['is_replaced']:
					# TODO: actually replace the player by an a(utonomous)i(ntern)
					player['is_replaced'] = True

				if not player['replace_reported']:
					player['replace_reported'] = True
					socketio.emit("info_player_replaced",
								  player_id,
								  namespace='/lobby',
								  to=tarot_rooms.get_room_code_by_room(room))
			# If the game hasn't yet started, remove the player from the slot
			else:
				room.get_players().pop(player_id)
				socketio.emit("info_player_removed",
							  player_id,
							  namespace='/lobby',
							  to=tarot_rooms.get_room_code_by_room(room))


def check_empty_room(room: TarotGameProxy):
	all_players_left = all(
		[player['is_replaced'] for player in room.get_players().values()]
	)
	if room.game_finished or all_players_left:
		room_code = tarot_rooms.get_room_code_by_room(room)
		socketio.close_room(room_code)
		del tarot_rooms[room_code]


socketio.start_background_task(target=run_background_update,
							   func=lobby_background_update,
							   interval=2)

lobby_namespace = LobbyNamespace('/lobby')
lobby_namespace.set_tarot_rooms(tarot_rooms)
socketio.on_namespace(lobby_namespace)
