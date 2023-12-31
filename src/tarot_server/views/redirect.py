from flask import Blueprint, redirect, url_for

views_redirect = Blueprint('redirect', 'tarot_server')


@views_redirect.route('/')
def root():
	return redirect(url_for('auth.login'))


@views_redirect.route('/not-implemented')
def not_implemented():
	return ('<h1 style="color: red">Function/Route not implemented</h1>'
			'<h2 style="color: black">You will be redirected now</h2>'
			'Please inform an admin when seeing this.',
			{"Refresh": "5; url='/'"})
