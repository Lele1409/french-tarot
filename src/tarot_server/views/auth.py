from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user

from src.tarot_server.utils.authentication import log_in, log_out, sign_up
from src.tarot_server.utils.forms import LoginForm, SignupForm

views_auth = Blueprint('auth', 'tarot_server')


# TODO: auto-redirect if already logged in


@views_auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('menu.menu'))

    signup_form = SignupForm()

    if signup_form.is_submitted() and \
            signup_form.agreements.validate(signup_form):
        if 'anon_signup-submit_anon' in request.form and \
                signup_form.anon_signup.validate(signup_form):
            email = sign_up(None, None, anon=True)[0]
            log_in(email)
            return redirect(url_for('menu.menu'))

        elif 'standard_signup-submit_standard' in request.form and \
                signup_form.standard_signup.validate(signup_form):
            sign_up(signup_form.standard_signup.email.data,
                    signup_form.standard_signup.password.data)
            return redirect(url_for('auth.login'))
    return render_template('auth/signup.html', form=signup_form)


@views_auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('menu.menu'))

    login_form = LoginForm()
    if login_form.validate_on_submit():
        # Login the user of which the login information has been verified
        log_in(login_form.email.data)
        return redirect(url_for('menu.menu'))
    return render_template('auth/login.html', form=login_form)


@views_auth.route('/logout')
def logout():
    """Discards the user's session login, thus logging them out on the server
	side and redirecting them to the login page."""

    # Formal logout
    log_out()
    # Visual logout
    return redirect(url_for('auth.login'))
