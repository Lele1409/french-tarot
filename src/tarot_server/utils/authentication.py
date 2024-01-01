from typing import Tuple

from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms.validators import ValidationError

from src.tarot_server.db.gen_credentials import gen_id, gen_pw
from src.tarot_server.db.roles import get_role_by_name
from src.tarot_server.server import tarot_server_db
from src.tarot_server.db.models import User


def validate_login_form_data(form, field):
	inputted_password: str = form.password.data
	inputted_email: str = form.email.data
	current_user: User = User.query.filter_by(email=inputted_email).first()
	is_registered: bool = current_user is not None and current_user.email == inputted_email
	if not is_registered:
		raise ValidationError('Email or password is incorrect...')
	is_correct_password: bool = check_password_hash(current_user.password,
													inputted_password)
	if not is_correct_password:
		raise ValidationError('Email or password is incorrect...')


def sign_up(email: str | None,
			password: str | None,
			anon: bool = False) -> Tuple[str, str] | None:
	"""Signs up a newly created user.
	:param email: The email to be used for creating the account;
	:param password: The password provided for creating the account, will be
	 stored as a scrypt hash;
	:param anon: If True, creates an anonymous account discarding any email or
	 password given."""

	# Get a unique id for the account
	uid = gen_id()

	# If the account is supposed to be an anonymous account
	if anon:
		upw = gen_pw()
		user_new = User(id=uid, email=uid, password=upw)
		# Set the user's role
		user_new.roles.append(
			get_role_by_name('anonymous'))  # TODO: can be removed?

	# Creating a standard account
	else:
		# Generate a hash with werkzeug.security.generate_password_hash()
		# using scrypt; during later login requests this hash can be validated
		# through the use of werkzeug.security.check_password_hash()
		hashed_password = generate_password_hash(password)
		user_new = User(id=uid, email=email, password=hashed_password)
		# Set the user's role
		user_new.roles.append(
			get_role_by_name('standard'))  # TODO: can be removed?

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
