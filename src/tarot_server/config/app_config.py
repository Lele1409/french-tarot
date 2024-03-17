# TODO: remove Flask-User and Flask-Mail

class AppConfigFlaskUser(object):
    """Configures mainly Flask-User and Flask-Mail.
	Currently, this config disables most of the default routes and
	most of the default functionality in Flask-User,
	but it is kept in for later potential use."""
    USER_APP_NAME = ("French-Tarot (though if you see this in the app I guess "
                     "there was an error)")
    USER_ENABLE_EMAIL = True
    USER_ENABLE_USERNAME = False
    USER_ENABLE_CHANGE_PASSWORD = False
    USER_ENABLE_CONFIRM_EMAIL = False
    USER_ENABLE_FORGOT_PASSWORD = False
    USER_ALLOW_LOGIN_WITHOUT_CONFIRMED_EMAIL = True
    USER_USER_SESSION_EXPIRATION = 36000

    USER_CHANGE_PASSWORD_URL = '/not-implemented'
    USER_CHANGE_USERNAME_URL = '/not-implemented'
    USER_CONFIRM_EMAIL_URL = '/not-implemented'
    USER_EDIT_USER_PROFILE_URL = '/not-implemented'
    USER_EMAIL_ACTION_URL = '/not-implemented'
    USER_FORGOT_PASSWORD_URL = '/not-implemented'
    USER_INVITE_USER_URL = '/not-implemented'
    USER_LOGIN_URL = '/login'
    USER_LOGOUT_URL = '/logout'
    USER_MANAGE_EMAILS_URL = '/not-implemented'
    USER_REGISTER_URL = '/signup'
    USER_RESEND_EMAIL_CONFIRMATION_URL = '/not-implemented'
    USER_RESET_PASSWORD_URL = '/not-implemented'

    USER_CHANGE_PASSWORD_TEMPLATE = ''
    USER_CHANGE_USERNAME_TEMPLATE = ''
    USER_EDIT_USER_PROFILE_TEMPLATE = ''
    USER_FORGOT_PASSWORD_TEMPLATE = ''
    USER_INVITE_USER_TEMPLATE = ''
    USER_LOGIN_TEMPLATE = ''
    USER_LOGIN_AUTH0_TEMPLATE = ''
    USER_MANAGE_EMAILS_TEMPLATE = ''
    USER_REGISTER_TEMPLATE = ''
    USER_RESEND_CONFIRM_EMAIL_TEMPLATE = ''
    USER_RESET_PASSWORD_TEMPLATE = ''

    USER_CONFIRM_EMAIL_TEMPLATE = ''
    USER_INVITE_USER_EMAIL_TEMPLATE = ''
    USER_PASSWORD_CHANGED_EMAIL_TEMPLATE = ''
    USER_REGISTERED_EMAIL_TEMPLATE = ''
    USER_RESET_PASSWORD_EMAIL_TEMPLATE = ''
    USER_USERNAME_CHANGED_EMAIL_TEMPLATE = ''
