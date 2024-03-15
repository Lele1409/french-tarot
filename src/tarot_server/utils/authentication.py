from typing import Tuple

from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash

from src.tarot_server.db.gen_credentials import gen_id, gen_pw
from src.tarot_server.db.models import User
from src.tarot_server.db.roles import get_role_by_name
from src.tarot_server.server import tarot_server_db


def sign_up(email: str | None,
            password: str | None,
            anon: bool = False) -> Tuple[str, str] | None:
    """Signs up a newly created user.
	:param email: The email to be used for creating the account;
	:param password: The password provided for creating the account, will be
	 stored as a scrypt hash;
	:param anon: If True, creates an anonymous account discarding any email or
	 password given.
	:returns None, or a tuple containing the generated email and password for
	 an anonymous account"""

    # Get a unique id for the account
    uid = gen_id()
    # And a unique password
    upw = gen_pw()

    # If the account is supposed to be an anonymous account
    if anon:
        user_new = User(id=uid, email=uid, password=upw)
        # Set the user's role
        user_new.roles.append(get_role_by_name('anonymous'))

    # Creating a standard account
    else:
        # Generate a hash with werkzeug.security.generate_password_hash()
        # using scrypt; during later login requests this hash can be validated
        # through the use of werkzeug.security.check_password_hash()
        hashed_password = generate_password_hash(password)
        user_new = User(id=str(uid), email=email, password=hashed_password)
        # Set the user's role
        user_new.roles.append(get_role_by_name('standard'))

    # Submit the data to the database
    tarot_server_db.session.add(user_new)
    tarot_server_db.session.commit()

    # Returns created values for reuse during login if signup was
    # for an anonymous user
    return (uid, upw) if anon else None


def log_in(email: str):
    logout_user()
    user = User.query.filter_by(email=email).first()
    login_user(user)


def log_out():
    logout_user()
