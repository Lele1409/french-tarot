from src.tarot_server.db.models import Role
from src.tarot_server.server import app_tarot_server, tarot_server_db


def add_new_role(role_name: str) -> None:
	with app_tarot_server.app_context():
		if Role.query.filter_by(name=role_name).first():
			return

		new_role = Role(name=role_name)
		tarot_server_db.session.add(new_role)
		tarot_server_db.session.commit()


def get_role_by_name(role_name):
	return (tarot_server_db.session.query(Role)
			.filter_by(name=role_name)
			.first())
