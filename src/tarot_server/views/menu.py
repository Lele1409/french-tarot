from flask import Blueprint, redirect, render_template, url_for
from flask_user import login_required

from src.tarot_server.utils.forms import LobbyCreateForm, LobbyJoinForm

views_menu = Blueprint('menu', 'tarot_server')


@views_menu.route('/menu', methods=['GET', 'POST'])
@login_required
def menu():
    menu_forms = {
        "LobbyJoin"  : LobbyJoinForm(),
        "LobbyCreate": LobbyCreateForm(),
    }

    if menu_forms['LobbyJoin'].validate_on_submit():
        code = menu_forms['LobbyJoin'].code.data
        return redirect(url_for('lobby.join', lobby_code=code))
    elif menu_forms['LobbyCreate'].validate_on_submit():
        return redirect(url_for('lobby.create'))
    return render_template('menu.html', forms=menu_forms)
