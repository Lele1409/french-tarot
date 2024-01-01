from flask import Blueprint, redirect, url_for

views_redirect = Blueprint('redirect', 'tarot_server')


@views_redirect.route('/')
def root():
	return redirect(url_for('auth.login'))
