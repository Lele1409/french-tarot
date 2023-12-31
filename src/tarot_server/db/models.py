from src.tarot_server.server import tarot_server_db as db

from flask_user import UserMixin


class User(db.Model, UserMixin):
	"""The user data model for the database. Every field is composed of:
	- id: a unique identifier for the user;
	- email: the email address entered at signup
	 (if the user is an anonymous user is equal to the id);
	- password: the password entered at signup;
	- acc_creation_date: the date the user was created;
	- roles: relationship pointing to the UserRoles table."""

	__tablename__ = 'users'

	# Identifier
	id = db.Column(db.Integer(),
				   primary_key=True)

	# User Authentication fields
	email = db.Column(db.String(255),
					  nullable=False,
					  unique=True)
	# TODO: add email_verification
	# email_confirmed_at = db.Column(db.DateTime())
	# TODO: add username
	# verification username = db.Column(db.String(50), nullable=False, unique=True)
	password = db.Column(db.String(255),
						 nullable=False)

	# User Authentication meta-fields
	acc_creation_date = db.Column(db.DateTime(timezone=True),
							  server_default=db.func.now())

	# User fields
	roles = db.relationship('Role',
							secondary='user_roles')

	# TODO: Keep? https://flask-user.readthedocs.io/en/latest/data_models.html
	# active = db.Column(db.Boolean())


class Role(db.Model):
	"""The Role data model for the database. Every field is composed of:
	- id: a unique identifier for the role;
	- name: the name of the role as further used within the application"""

	__tablename__ = 'roles'

	id = db.Column(db.Integer(),
				   primary_key=True,
				   unique=True,
				   autoincrement=True)
	name = db.Column(db.String(50),
					 unique=True,
					 nullable=False)


# Define the UserRoles association table
class UserRoles(db.Model):
	"""The UserRoles data model for the database. Every field is composed of:
	- id: a unique identifier for the role assignment;
	- user_id: the id of the user that owns the role;
	- role_id: the id of the role assigned to the user."""

	__tablename__ = 'user_roles'

	# Identifier
	id = db.Column(db.Integer(),
				   primary_key=True,
				   unique=True,
				   autoincrement=True)

	# User and connected role
	user_id = db.Column(db.Integer(),
						db.ForeignKey('users.id', ondelete='CASCADE'),
						nullable=False)
	role_id = db.Column(db.Integer(),
						db.ForeignKey('roles.id', ondelete='CASCADE'),
						nullable=False)
