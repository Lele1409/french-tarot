from typing import Tuple

from flask_login import login_user, logout_user
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.security import check_password_hash, generate_password_hash

from src.tarot_server.db.gen_credentials import gen_id, gen_pw
from src.tarot_server.db.roles import get_role_by_name
from src.tarot_server.server import tarot_server_db
from src.tarot_server.db.models import User


def validate_form_data_signup(form: dict[str, str]) -> str:
	"""Verifies that the form is valid, and if not, defines the error message
	to be shown to the user.
	:arg form: The form to be validated in this function
	:returns an empty string if the form is valid, otherwise the string
	contains an error message"""

	error_message = ''

	# First check if the user ticked the agree box,
	# any other error will overwrite this one
	if form['agreement'] != 'on':
		error_message = 'Please agree...'

	# Check for other errors
	if form['signup-anonymous'] == '':
		if form['signup-standard'] == '':
			error_message = 'Please choose only one signup method...'
	elif form['signup-standard'] != '':
		error_message = 'Please choose any signup method...'
	elif form['email'] == '' \
			or form['reenter-email'] == '' \
			or form['password'] == '' \
			or form['reenter-password'] == '':
		error_message = 'Please fill in all the fields...'
	elif form['email'] != form['reenter-email']:
		error_message = 'Email addresses do not match...'
	elif form['password'] != form['reenter-password']:
		error_message = 'Passwords do not match...'

	# Check if email is a valid email
	# and if the password is a secure password  # TODO

	# Check if email already exists
	if form['signup-standard'] == '' and \
			(tarot_server_db.session
					 .query(User)
					 .filter_by(email=form['email'])
					 .first().email == form['email']):
		error_message = 'Email already registered, please login...'

	return error_message


def validate_form_data_login(form: ImmutableMultiDict[str, str]) -> str:
	"""Verifies that the form (for logging into an existing account) is valid
	:arg form: the form to be validated in this function
	:returns an empty string if the form is valid, otherwise the string
	contains an error message"""

	if form['email'] == '' \
			or form['password'] == '':
		return 'Please fill in all the fields...'

	if '@' not in form['email']:
		return 'Please enter a valid email'

	current_user = (User.query
					.filter_by(email=form['email'])
					.first())

	if current_user is None:
		return 'Account with this email has not been created: please signup first...'

	is_email_in_db = current_user.email == form['email']

	if not is_email_in_db:
		return 'Account with this email has not been created: please signup first...'

	is_right_password: bool = check_password_hash(current_user.password,
												  form['password'])

	if not is_right_password:
		return 'Data invalid, please try again...'

	return ''


def sign_up(email: str | None,
			password: str | None,
			anon: bool = False) -> Tuple[str, str] | None:
	"""Signs up a newly created user.
	:arg email: The email to be used for creating the account;
	:arg password: The password provided for creating the account, will be
	 stored as a scrypt hash;
	:arg anon: If True, creates an anonymous account discarding any email or
	 password given."""

	# Get a unique id for the account
	uid = gen_id()

	# If the account is supposed to be an anonymous account
	if anon:
		upw = gen_pw()
		user_new = User(id=uid, email=uid, password=upw)
		# Set the user's role
		user_new.roles.append(get_role_by_name('anonymous'))  # TODO: can be removed?

	# Creating a standard account
	else:
		# Generate a hash with werkzeug.security.generate_password_hash()
		# using scrypt; during later login requests this hash can be validated
		# through the use of werkzeug.security.check_password_hash()
		hashed_password = generate_password_hash(password)
		user_new = User(id=uid, email=email, password=hashed_password)
		# Set the user's role
		user_new.roles.append(get_role_by_name('standard'))  # TODO: can be removed?

	# Submit the data to the database
	tarot_server_db.session.add(user_new)
	tarot_server_db.session.commit()

	# Returns created values for reuse during login if signup was
	# for an anonymous user
	return (uid, upw) if anon else None


def log_in(email: str, password: str, anon: bool = False):
	user = User.query.filter_by(email=email).first()
	login_user(user)


def log_out():
	logout_user()


if __name__ == '__main__':
	sign_up(True)
