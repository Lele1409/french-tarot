import secrets

from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user
from flask_user import login_required

from src.config.configLoader import config_tarot_server as config
from src.tarot_server.server import socketio
from src.tarot_server.utils.background_runner import run_background_update
from src.tarot_server.utils.proxies.rooms_proxy import TarotRooms
from src.tarot_server.utils.proxies.tarot_game_proxies import TarotGameProxy, \
    TarotPlayerProxy
from src.tarot_server.views.lobby_websocket import LobbyNamespace, \
    update_client_player_list

views_lobby = Blueprint('lobby', 'tarot_server', url_prefix='/lobby')

tarot_rooms: TarotRooms[TarotGameProxy] = TarotRooms()

# TODO: sanitize/standardize names for room, room_code, player...
#  (lobby => room ?? room => lobby)

# TODO: COMMENT!!

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
		return redirect(url_for('lobby.room_does_not_exist'))
	if not tarot_rooms.is_joignable(current_user.id, lobby_code):
		# TODO: display some sort of information to the user
		#  about why he wasn't able to join, and/or redirect
		#  him to an observer page
		return redirect(url_for('lobby.game_is_running'))
	return render_template('lobby.html', code=lobby_code)


@views_lobby.route('/<string:lobby_code>/game')
@login_required
def game(lobby_code=None):
	return render_template('game.html', code=lobby_code)


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

		player_id = room.get_player_id_by_player(player)
		room_code = tarot_rooms.get_room_code_by_room(room)

		if not room.game_running:
			# If the game hasn't yet started, remove the player from the slot,
			# since he can simply rejoin if needed
			room.remove_player(player_id)
			update_client_player_list(room_code)
			continue

		# Inform players about another player's disconnect
		if player.get_time_since_last_seen() > 10:  # TODO: configurability
			if not player['disconnect_reported']:
				player['disconnect_reported'] = True
				update_client_player_list(room_code)

		# Replace player disconnected for too long if the game is already running
		if player.get_time_since_last_seen() > 30:  # TODO: configurability
			if not player['is_ai']:
				# TODO: actually replace the player by an a(utonomous)i(ntern)
				player.replace_by_ai()

			if not player['replace_reported']:
				player['replace_reported'] = True
				update_client_player_list(room_code)


def check_empty_room(room: TarotGameProxy):
	# Is true when all players have is_ai=True, or if there are no players
	# left on which you could check
	all_players_left = all(
		[player['is_ai'] for player in room.get_players().values()]
	)
	if room.game_can_be_deleted or all_players_left:
		room_code = tarot_rooms.get_room_code_by_room(room)
		socketio.close_room(room_code)
		tarot_rooms.remove(room_code)


socketio.start_background_task(target=run_background_update,
							   func=lobby_background_update,
							   interval=1)

lobby_namespace = LobbyNamespace('/lobby')
lobby_namespace.set_tarot_rooms(tarot_rooms)
socketio.on_namespace(lobby_namespace)
