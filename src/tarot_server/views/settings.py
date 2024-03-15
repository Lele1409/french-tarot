from flask import Blueprint, render_template
from flask_user import login_required

views_settings = Blueprint('settings', 'tarot_server')


@views_settings.route('/settings')
@login_required
def settings():
    return render_template('settings.html')
