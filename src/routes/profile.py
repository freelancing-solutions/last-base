from flask import Blueprint, render_template, send_from_directory, request, redirect, url_for, flash
from pydantic import ValidationError

from src.authentication import login_required
from src.database.models.game import GameAuth, GameIDS
from src.database.models.profile import ProfileUpdate
from src.database.models.users import User
from src.utils import static_folder
from src.main import user_controller, game_controller

profile_route = Blueprint('profile', __name__)


@profile_route.get('/dashboard/profile')
@login_required
async def get_profile(user: User):
    context = dict(user=user)

    data = await user_controller.get_profile_by_game_id(game_id=user.game_id)
    context = dict(profile=data)
    return render_template('profile.html', **context)


@profile_route.post('/dashboard/profile')
@login_required
async def update_profile(user: User):
    try:

        updated_profile = ProfileUpdate(request.form)
    except ValidationError as e:
        pass


@profile_route.get('/dashboard/settings')
@login_required
async def get_settings(user: User):
    context = dict(user=user)

    data = await user_controller.get_profile_by_game_id(game_id=user.game_id)
    context = dict(profile=data)
    return render_template('config.html', **context)


@profile_route.get('/dashboard/verification-request')
@login_required
async def get_verification(user: User):
    context = dict(user=user)
    return render_template('verification.html', **context)


@profile_route.post('/dashboard/verification-request')
@login_required
async def do_verification(user: User):
    context = dict(user=user)
    try:
        game_auth = GameAuth(**request.form)
        game_data = await game_controller.create_account_verification_request(game_data=game_auth)
        _message = "Account Verification Data sent successfully your account will be verified shortly"
        flash(message=_message, category="success")
        return redirect(location=url_for('profile.get_settings'))
    except ValidationError as e:
        flash(message=f"there was an error: {str(e)}", category='success')
        return redirect(location=url_for('profile.get_settings'))


@profile_route.get('/dashboard/gift-codes')
@login_required
async def get_gift_codes(user: User):
    context = dict(user=user)
    return render_template('gift_codes.html', **context)


@profile_route.post('/dashboard/gift-codes')
@login_required
async def redeem_codes(user: User):
    context = dict(user=user)
    try:
        game_ids = GameIDS(request.form)
    except ValidationError as e:
        pass

    return render_template('gift_codes.html', **context)


@profile_route.get('/dashboard/market-listing')
@login_required
async def get_market_listing(user: User):
    context = dict(user=user)
    return render_template('market_listing.html', **context)
