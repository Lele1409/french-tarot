from flask import Blueprint, render_template
from flask_user import login_required

views_menu = Blueprint('menu', 'tarot_server')


@views_menu.route('/menu')
@login_required
def menu():
	return render_template('menu.html')
