"""Contains all the forms used in the application."""
import string

import wtforms
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms.fields.simple import BooleanField, PasswordField, StringField, \
	SubmitField
from wtforms.validators import Email, EqualTo, InputRequired, Optional, \
	Regexp, ValidationError

from src.config.configLoader import config_tarot_server as config
from src.tarot_server.db.models import User
from src.tarot_server.utils.string_manip import count_any_occurrence as c_a_o

# TODO: break down file in multiple files in one /form directory

SAFE_SPECIAL_CHARS = config['Credentials']['safe_special_chars']


class NotEqualTo(object):
	"""Derived class from wtforms.validators.EqualTo.
	This validator checks that two fields are not equal to each other.

	:param fieldname: The name of the field to compare to.
	:param message: Error message to raise in case of a validation error.
	 Can be interpolated with `%(other_label)s` and `%(other_name)s`
	 to provide a more helpful error. """

	def __init__(self, fieldname, message=''):
		self.fieldname = fieldname
		self.message = message

	def __call__(self, form, field):
		try:
			other = form[self.fieldname]
		except KeyError:
			raise ValidationError(
				field.gettext(f"Invalid fieldname {self.fieldname}"))
		if field.data == other:
			d = {
				'other_label': hasattr(other,
									   'label') and other.label.text or self.fieldname,
				'other_name' : self.fieldname
			}
			message = self.message
			if not message:
				message = field.gettext(
					f'Field must be equal to {d['other_name']}')
			raise ValidationError(message)


class ValidLoginData:
	def __init__(self, message=''):
		self.message = message

	def __call__(self, form, field):
		inputted_email = form.email.data
		inputted_password = form.password.data

		current_user: User = User.query.filter_by(email=inputted_email).first()
		is_registered: bool = (current_user is not None
							   and current_user.email == inputted_email)

		if not is_registered:
			raise ValidationError(self.message)

		is_anonymous_user: bool = current_user.has_roles('anonymous')

		if is_anonymous_user:
			raise ValidationError(self.message)

		is_correct_password: bool = check_password_hash(current_user.password,
														inputted_password)

		if not is_correct_password:
			raise ValidationError(self.message)


class EmailNotInUse:
	def __init__(self, message=''):
		self.message = message

	def __call__(self, form, field):
		if User.query.filter_by(email=field.data).first() is not None:
			raise ValidationError(self.message)


class SecurePassword:
	def __init__(self):
		# Load values from the config
		c = config['Credentials.Submitted']
		self.min_length = int(c['min_length'])
		self.max_length = int(c['max_length'])
		self.min_lower_chars = int(c['min_lower_chars'])
		self.min_upper_chars = int(c['min_upper_chars'])
		self.min_digits = int(c['min_digits'])
		self.min_special_chars = int(c['min_special_chars'])
		self.can_overlap_with_mail = bool(c['can_overlap_with_mail'] == 'True')

	def __call__(self, form, field):
		# Define the error message to show to the user in case of a failed test
		self.messages = [
			f"Password length: {self.min_length}-{self.max_length}",
			f"Lowercase characters: >{self.min_lower_chars}",
			f"Uppercase characters: >{self.min_upper_chars}",
			f"Digits: >{self.min_digits}",
			f"Special characters: >{self.min_special_chars}, "
			f"can be used: {SAFE_SPECIAL_CHARS}",
			f"The password cannot contain parts of the email-address..."]

		# Get the data from the form
		password: str = field.data
		email: str = form.email.data

		# Test all conditions for defining a secure password
		if not self.min_length <= len(password) <= self.max_length:
			raise ValidationError(self.messages[0])
		if not c_a_o(password, string.ascii_lowercase) >= self.min_lower_chars:
			raise ValidationError(self.messages[1])
		if not c_a_o(password, string.ascii_uppercase) >= self.min_upper_chars:
			raise ValidationError(self.messages[2])
		if not c_a_o(password, string.digits) >= self.min_digits:
			raise ValidationError(self.messages[3])
		if not c_a_o(password, SAFE_SPECIAL_CHARS) >= self.min_special_chars:
			raise ValidationError(self.messages[4])

		# If the test is enabled in the config
		if (not self.can_overlap_with_mail and
				# Test for overlaps with the password on the part
				# of the email before the '@' symbol
				any([s in password for s in email.split('@')[0].split('.')])):
			# Show a different error for this test
			raise ValidationError(self.messages[5])


class LoginForm(FlaskForm):
	email = StringField(
		'Enter your email-address...',
		validators=[InputRequired(
			'Please enter your email-address...')]
	)
	password = PasswordField(
		'Enter your password...',
		validators=[InputRequired(
			'Please enter your password...')]
	)
	submit = SubmitField(
		'Submit',
		validators=[InputRequired(
			'Please submit...'),
			ValidLoginData(
				'Email or password is incorrect...')]
	)


class SignupStandardForm(FlaskForm):
	submit_standard = SubmitField(
		'Signup',
		validators=[Optional()]
	)

	# Inputs
	email = StringField(
		'Enter your email-address...',
		validators=[InputRequired(
			'Please enter your email-address...'),
			Email(
				granular_message=True),
			Regexp(
				'[a-zA-Z0-9_' + SAFE_SPECIAL_CHARS + '@.' + ']',
				message=f'Please only use letters, numbers and {SAFE_SPECIAL_CHARS}'),
			EmailNotInUse(
				'Email address is already registered, please log in...')
		]
	)
	reenter_email = StringField(
		'Reenter your email-address...',
		validators=[InputRequired(
			'Please reenter your email-address...'),
			EqualTo(
				'email',
				message='Email-addresses must match...')
		]
	)

	password = PasswordField(  # TODO: must be a secure password
		'Enter your password...',
		validators=[InputRequired(
			'Please enter a password...'),
			SecurePassword(),
			Regexp('[a-zA-Z0-9_' + SAFE_SPECIAL_CHARS + ']',
				   message=f'Please only use letters, numbers and {SAFE_SPECIAL_CHARS}')
		]
	)
	reenter_password = PasswordField(
		'Reenter your password...',
		validators=[InputRequired(
			'Please reenter a password...'),
			EqualTo(
				'password',
				message='Passwords must match...')
		]
	)


class SignupAnonForm(FlaskForm):
	# Submitters
	submit_anon = SubmitField(
		'Signup anonymously',
		validators=[Optional()]
	)


class SignupForm(FlaskForm):
	# Make bigger form with both other forms
	anon_signup = wtforms.FormField(SignupAnonForm)
	standard_signup = wtforms.FormField(SignupStandardForm)

	# Checkbox
	agreements = BooleanField(
		'Agreements',
		validators=[InputRequired('To proceed, please agree...')]
	)


lobby_code_length = str(int(config['Lobby.Security']['code_length']) // 2)


class LobbyJoinForm(FlaskForm):
	code = StringField(
		validators=[
			InputRequired('Please enter a code...'),
			Regexp(f"[0-9A-F]{'{' + lobby_code_length + '}'}",
				   message="Please enter a valid code...")]
	)

	submit_join = SubmitField(
		'(Re-)Join lobby with code',
		validators=[InputRequired('Please submit...')]
	)


class LobbyCreateForm(FlaskForm):
	submit_create = SubmitField(
		'Create lobby',
		validators=[InputRequired('Please submit...')]
	)
