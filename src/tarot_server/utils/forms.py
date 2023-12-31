"""Contains all the forms used in the application."""

from flask_wtf import FlaskForm
from wtforms.fields.simple import PasswordField, StringField, SubmitField
from wtforms.validators import Email, InputRequired

from src.tarot_server.utils.authentication import validate_login_form


class LoginForm(FlaskForm):
	email = StringField('Enter your email-address...',
						validators=[InputRequired()])
	password = PasswordField('Enter your password...',
							 validators=[InputRequired()])
	submit = SubmitField('Submit', validators=[validate_login_form])


class SignupForm(FlaskForm):
	email = StringField('Enter your email-address...',
						validators=[InputRequired(),
									Email(message='Please enter a valid email...',
										  check_deliverability=True)])