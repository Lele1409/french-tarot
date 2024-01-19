"""Set up the backend webserver using Flask to serve the user the tarot
application."""

import os

from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager

from src.config.appConfig import AppConfigFlaskUser
from src.config.configLoader import config_tarot_server

# TODO: refactor file to have configuration all in one folder, and different
#  functions for different steps of the app creation in their own

# Instantiate the application and configure
app_tarot_server = Flask('tarot_server',
						 template_folder=os.path.abspath(
							 r'./tarot_server/templates'),
						 static_folder=os.path.abspath(
							 r'./tarot_server/static'
						 ),
						 instance_path=os.path.abspath(
							 r'./tarot_server/instance')
						 )

# Set the secret keys
app_tarot_server.config['SECRET_KEY'] = \
	os.environ.get('APP_TAROT_SERVER_SECRET_KEY')
app_tarot_server.config['WTF_CSRF_SECRET_KEY'] = \
	os.environ.get('APP_TAROT_SERVER_CSRF_SECRET_KEY')

# Instantiate the websockets
socketio = SocketIO(app_tarot_server,
					logger=True)

# Instantiate the database
tarot_server_db = SQLAlchemy()


def run_tarot_server() -> None:
	"""Run the tarot webserver
	:returns: None
	"""

	# Connect to the database
	db_name = config_tarot_server['Database']['Name']
	app_tarot_server.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_name}'
	tarot_server_db.init_app(app_tarot_server)

	# If the file hasn't been created yet (or it got deleted)
	# -> Can be checked by looking in the 'instance' folder
	#    and searching for the file.
	# First, we need to import the model classes because otherwise
	# the tables are not created in the database
	from src.tarot_server.db.models import User, Role, UserRoles  # NOQA
	if not os.path.exists(os.path.abspath(r'./tarot_server/instance' + db_name)):

		# Create the file with the given context
		with app_tarot_server.app_context():
			tarot_server_db.create_all()

		# In the newly created file, add roles to for the application
		# to assign to users
		from src.tarot_server.db.roles import add_new_role

		roles: str = config_tarot_server['Database']['Roles']
		for role in roles.split('|'):
			add_new_role(role)

	# Import and register all blueprints
	# (adds all configured views to the app)
	from src.tarot_server.views.auth import views_auth
	from src.tarot_server.views.redirect import views_redirect
	from src.tarot_server.views.menu import views_menu
	from src.tarot_server.views.settings import views_settings
	from src.tarot_server.views.errors import views_errors
	from src.tarot_server.views.lobby import views_lobby

	app_tarot_server.register_blueprint(views_redirect)
	app_tarot_server.register_blueprint(views_auth)
	app_tarot_server.register_blueprint(views_menu)
	app_tarot_server.register_blueprint(views_settings)
	app_tarot_server.register_blueprint(views_errors)
	app_tarot_server.register_blueprint(views_lobby)

	# Disable Flask-Mail
	app_tarot_server.config['USER_EMAIL_SENDER_EMAIL'] = 'no-reply@localhost'

	# Add a user manager
	app_tarot_server.config.from_object(AppConfigFlaskUser)
	UserManager(app_tarot_server, tarot_server_db, User)

	# Run the server with websocket-capability
	socketio.run(
		app=app_tarot_server,
		allow_unsafe_werkzeug=config_tarot_server['Server']['isDebug'],
		debug=config_tarot_server['Server']['isDebug']
	)
