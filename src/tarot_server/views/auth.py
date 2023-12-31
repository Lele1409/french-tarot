from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from src.tarot_server.utils.authentication import log_in, log_out, sign_up, \
	validate_form_data_signup
from src.tarot_server.utils.forms import LoginForm

views_auth = Blueprint('auth', 'tarot_server')


@views_auth.route('/signup', methods=['GET', 'POST'])
def signup():
	# When the user loads the page return the HTML
	if request.method == 'GET':
		# If the user is already logged in
		if current_user.is_authenticated:
			return redirect(url_for('menu.menu'))

		return render_template('auth/signup.html')

	# Get data from submitted form
	form_data = {
		'email'           : request.form.get('email', '').lower(),
		'reenter-email'   : request.form.get('reenter-email', '').lower(),
		'password'        : request.form.get('password', ''),
		'reenter-password': request.form.get('reenter-password', ''),
		'agreement'       : request.form.get('agreement', 'off'),
		'signup-standard' : request.form.get('signup-standard', None),
		'signup-anonymous': request.form.get('signup-anonymous', None)
	}

	# Check if the form data is valid, if it isn't: flash the user an error
	error_message = validate_form_data_signup(form_data)
	if error_message:
		flash(error_message, 'error')
		# Do not send back the passwords
		# and do not send back which submit-button was pressed
		del form_data['password']
		del form_data['reenter-password']
		del form_data['signup-anonymous']
		del form_data['signup-standard']
		return render_template('auth/signup.html', entered_values=form_data)

	# Check if the user chose not to create an account but to
	# signup for an automatically generated account
	is_anonymous_signup = 'signup-anonymous' in request.form

	# If the user chose the anonymous signup, add user to the database
	# and log in the anonymous user
	if is_anonymous_signup:
		uid, pw = sign_up(None, None, anon=True)
		log_in(uid, pw, anon=True)

	# If the user chose to create a real account, add user to the database
	else:
		sign_up(form_data['email'], form_data['password'])

	# The user's account is now created; send the user to the login page,
	# if they're anonymous they'll be automatically redirected
	flash('Account created, you will be redirected now.', 'success')
	return render_template('auth/signup.html'), {"Refresh": "1.5; url='/'"}


@views_auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		log_in(form.email.data, form.password.data)
		return redirect(url_for('menu.menu'))
	return render_template('auth/login.html', form=form)


@views_auth.route('/logout')
def logout():
	"""Discards the user's session cookie, thus logging them out on the server
	side and redirecting them to the login page"""

	# Formal logout
	log_out()
	# Visual logout
	return redirect(url_for('auth.login'))
