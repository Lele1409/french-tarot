from flask import Blueprint, render_template
from flask_user import login_required

from src.tarot_server.utils.forms import LobbyCreateForm, LobbyJoinForm

views_menu = Blueprint('menu', 'tarot_server')


@views_menu.route('/menu')
@login_required
def menu():
	forms = {
		"LobbyJoin": LobbyJoinForm(),
		"LobbyCreate": LobbyCreateForm(),
	}
	return render_template('menu.html', forms=forms)
