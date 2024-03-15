import random
import string

from src.config.config_loader import config_tarot_server
from src.tarot_server.db.models import User
from src.tarot_server.server import tarot_server_db


def id_is_used(uid) -> bool:
	"""Checks whether an id is already used in the database as to ensure
	the uniqueness of all the ids.
	:returns: A boolean, True if the id can be used, False otherwise"""

	is_used: bool = (tarot_server_db.session.query(User)
					 .filter_by(id=uid)
					 .first() == uid)

	return is_used


def gen_id() -> str:
	"""Generates a random string of digits and checks if it isn't already in use.
	:returns: A string with a length specified in the server config"""

	resulting_string = ''
	while id_is_used(resulting_string) or not resulting_string:
		id_number_len: int = \
			int(config_tarot_server['Credentials.Generation']['ID.Num_Len'])
		id_numbers: list = \
			[random.choice(string.digits) for _ in range(id_number_len)]
		resulting_string: str = ''.join(id_numbers)
	return resulting_string


def gen_pw() -> str:
	"""Generates a random string of letters and digits.
	:returns: A string with a length specified in the server config"""
	chars: str = string.ascii_letters + string.digits
	pw_len: int = int(config_tarot_server['Credentials.Generation']['PW.Char_Len'])
	random_chars: list = [random.choice(chars) for _ in range(pw_len)]
	resulting_string: str = ''.join(random_chars)
	return resulting_string
