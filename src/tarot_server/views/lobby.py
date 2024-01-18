import secrets

from flask import Blueprint, redirect, url_for

from src.config.configLoader import config_tarot_server

views_lobby = Blueprint('lobby', 'tarot_server', url_prefix='/lobby')


@views_lobby.route('/')
def create():
	code_len = int(config_tarot_server['Lobby.Security']['code_length'])//2
	code = secrets.token_hex(code_len).upper()
	return redirect(url_for('lobby.join', lobby_code=code))


@views_lobby.route('/<string:lobby_code>')
def join(lobby_code=None):
	return f"joined lobby with code '{lobby_code}'"
