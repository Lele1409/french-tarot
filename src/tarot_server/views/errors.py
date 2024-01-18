from flask import Blueprint, render_template

views_errors = Blueprint('errors', 'tarot_server')


@views_errors.app_errorhandler(403)
def error_403_forbidden():
	return render_template('errors/403.html'), 403


@views_errors.app_errorhandler(404)
def error_404_page_not_found():
	return render_template('errors/404.html'), 404


@views_errors.route('/not-implemented')
@views_errors.app_errorhandler(501)
def error_501_not_implemented():
	return render_template('errors/501.html'), 501
