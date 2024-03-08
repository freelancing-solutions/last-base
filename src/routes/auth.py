from datetime import timedelta, datetime

from flask import Blueprint, render_template, send_from_directory, flash, request, make_response, redirect, Response, \
    url_for
from pydantic import ValidationError

from src.database.models.auth import Auth, RegisterUser
from src.database.models.users import User, CreateUser

from src.logger import init_logger
from src.main import user_controller

auth_route = Blueprint('auth', __name__)
auth_logger = init_logger('auth_logger')
REMEMBER_ME_DELAY = 60 * 60 * 24 * 30

async def create_response(redirect_url, message=None, category=None) -> Response:
    response = make_response(redirect(redirect_url))
    if message and category:
        flash(message=message, category=category)
    return response


@auth_route.get('/login')
async def get_auth():
    context = {}
    return render_template('login.html', **context)


@auth_route.post('/login')
async def do_login():
    try:
        auth_user = Auth(**request.form)
    except ValidationError as e:
        auth_logger.error(str(e))
        return await create_response(url_for('auth.get_auth'), 'Login failed. Check your username and password.',
                                     'danger')

    login_user: User | None = await user_controller.login(username=auth_user.username, password=auth_user.password)
    if login_user and login_user.username == auth_user.username:
        response = await create_response(url_for('profile.get_profile'))

        # Setting Loging Cookie
        delay = REMEMBER_ME_DELAY if auth_user.remember == "on" else 30
        expiration = datetime.utcnow() + timedelta(minutes=delay)
        response.set_cookie('auth', value=login_user.game_id, expires=expiration, httponly=True)

        if not login_user.account_verified:
            _ = await user_controller.send_verification_email(user=login_user)
            flash(message="A verification email has been sent please verify your email", category="danger")
        return response
    else:
        return await create_response(url_for('auth.get_auth'),
                                     'Login failed. you may not be registered in this system', 'danger')


@auth_route.get('/dashboard/logout')
async def do_logout():
    """

    :return:
    """
    # TODO - CHECK IF USER IS ALREADY LOGGED IN
    response = await create_response(url_for('home.get_home'))
    response.delete_cookie('auth')
    flash(message='You have been successfully logged out.', category='danger')
    return response


@auth_route.get('/password-reset')
async def get_password_reset():
    context = {}
    return render_template('password_reset.html', **context)


@auth_route.post('/password-reset')
async def do_password_reset():
    context = {}
    # Check if User Email is available
    # Send Message to User with a link to reset password
    # Flash the message that email was sent with proper details never indicate failure
    flash(message="Message with a link to reset your password has been sent", category='success')
    return render_template('index.html', **context)


@auth_route.get('/register')
async def get_register():
    context = {}
    return render_template('register.html', **context)


@auth_route.post('/register')
async def do_register():
    """
        **do_register**

    :return:
    """
    # TODO - CHECK IF USER IS ALREADY LOGGED IN
    try:
        register_user: RegisterUser = RegisterUser(**request.form)
    except ValidationError as e:
        auth_logger.error(str(e))
        return await create_response(url_for('auth.get_register'), 'Please fill in all the required fields.', 'danger')

    user_exist: User | None = await user_controller.get_by_email(email=register_user.email)
    # user bool test for the conditions necessary to validate the user
    if user_exist:
        flash(message='User Already Exist please login', category='success')
        return await create_response(url_for('auth.get_auth'))
    print(f"Registering user : {register_user}")
    user_data: CreateUser = CreateUser(**register_user.dict(exclude={'terms'}))

    _user_data: User | None = await user_controller.post(user=user_data)
    if _user_data:
        flash(message='Account Successfully created please login', category='success')
        response: Response = await create_response(url_for('auth.get_auth'))
        expiration = datetime.utcnow() + timedelta(minutes=30)
        response.set_cookie('auth', value=user_data.game_id, expires=expiration, httponly=True)
        return response

    flash(message='failed to create new user try again later', category='danger')
    return await create_response(url_for('home.get_home'))
