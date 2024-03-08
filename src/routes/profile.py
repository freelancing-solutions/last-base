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
    data = await user_controller.get_profile_by_game_id(game_id=user.game_id)
    context = dict(profile=data, user=user)
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
    context.update(profile=data)
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
    """
        this method only adds game ids into database
        only unique game ids are added errors are ignored
    :param user:
    :return:
    """
    context = dict(user=user)
    try:
        game_ids_input = request.form.get('game_ids', '').strip()
        if ',' in game_ids_input:
            game_ids_list = [id.strip() for id in game_ids_input.split(',') if id.strip()]
        else:
            game_ids_list = [game_ids_input]

        for game_id in game_ids_list:
            if len(game_id) != 8:
                flash("Please provide valid 8-character Game IDs.", "danger")
                return render_template('gift_codes.html', **context)

        game_ids = GameIDS(game_id_list=game_ids_list)
        completed = await game_controller.add_game_ids(game_ids=game_ids)

        if completed:
            flash("Successfully added game IDs. New codes will be automatically redeemed as they become available.",
                  "success")
        else:
            _message: str = "could not verify if game ids where added please try again"
            flash(message=_message, category="danger")

    except ValidationError as e:
        flash(f"Error: {str(e)}", "danger")

    return render_template('gift_codes.html', **context)


@profile_route.get('/dashboard/market-listing')
@login_required
async def get_market_listing(user: User):
    context = dict(user=user)
    return render_template('market_listing.html', **context)
