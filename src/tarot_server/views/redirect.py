from flask import Blueprint, redirect, render_template, url_for

views_redirect = Blueprint('redirect', 'tarot_server')


@views_redirect.route('/')
def root():
	return redirect(url_for('auth.login'))


@views_redirect.route('/users')
def users():
	return redirect(url_for('errors.error_501_not_implemented'))
	return render_template('users.html')
