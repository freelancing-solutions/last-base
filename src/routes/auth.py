from flask import Blueprint, render_template, send_from_directory, flash
from src.utils import static_folder

auth_route = Blueprint('auth', __name__)


@auth_route.get('/login')
def get_auth():
    context = {}
    return render_template('login.html', **context)


@auth_route.get('/password-reset')
def get_password_reset():
    context = {}
    return render_template('password_reset.html', **context)


@auth_route.post('/password-reset')
def do_password_reset():
    context = {}
    # Check if User Email is available
    # Send Message to User with a link to reset password
    # Flash the message that email was sent with proper details never indicate failure
    flash(message="Message with a link to reset your password has been sent", category='success')
    return render_template('index.html', **context)
