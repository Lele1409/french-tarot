"""Contains all the forms used in the application."""

import wtforms
from flask_wtf import FlaskForm
from wtforms.fields.simple import BooleanField, PasswordField, StringField, \
	SubmitField
from wtforms.validators import Email, EqualTo, InputRequired, Optional, \
	StopValidation, ValidationError

from src.tarot_server.utils.authentication import validate_login_form_data


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


class EndValidation:
	def __call__(self):
		raise StopValidation


# TODO: add placeholder to input fields

# TODO: add verification for secure password with criteria,
#  and secure with no overlap with email

class LoginForm(FlaskForm):
	email = StringField(
		'Enter your email-address...',
		validators=[InputRequired('Please enter your email-address...')]
	)
	password = PasswordField(
		'Enter your password...',
		validators=[InputRequired('Please enter your password...')]
	)
	submit = SubmitField(
		'Submit',
		validators=[InputRequired('Please submit...'),
					validate_login_form_data]
	)


class SignupStandardForm(FlaskForm):
	submit_standard = SubmitField(
		'Signup',
		validators=[Optional()]
	)

	# Inputs
	email = StringField(
		'Enter your email-address...',
		validators=[InputRequired('Please enter your email-address...'),
					Email(
						granular_message=True)
					]
	)
	reenter_email = StringField(
		'Reenter your email-address...',
		validators=[InputRequired('Please reenter your email-address...'),
					EqualTo(
						'email',
						message='Email-addresses must match...')
					]
	)

	password = PasswordField(  # TODO: must be a secure password
		'Enter your password...',
		validators=[InputRequired('Please enter a password...')]
	)
	reenter_password = PasswordField(
		'Reenter your password...',
		validators=[InputRequired('Please reenter a password...'),
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
