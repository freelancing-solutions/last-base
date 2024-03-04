from flask import Blueprint, render_template, send_from_directory, flash, request, make_response, redirect, Response, \
    url_for
from pydantic import ValidationError

from src.database.models.auth import Auth
from src.utils import static_folder
from src.logger import init_logger

auth_route = Blueprint('auth', __name__)
auth_logger = init_logger('auth_logger')

async def create_response(redirect_url, message=None, category=None) -> Response:
    response = make_response(redirect(redirect_url))
    if message and category:
        flash(message=message, category=category)
    return response

@auth_route.get('/login')
def get_auth():
    context = {}
    return render_template('login.html', **context)


@auth_route.post('/login')
async def do_login():
    context = {}
    auth_user = Auth(**request.form)
    try:
        auth_user = Auth(**request.form)
    except ValidationError as e:
        auth_logger.error(str(e))
        return await create_response(url_for('auth.get_login'), 'Login failed. Check your username and password.',
                                     'danger')

    print(auth_user)
    flash(message='Successfully logged in', category='success')
    return render_template('index.html')


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
