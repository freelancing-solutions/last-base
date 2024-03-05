from flask import Blueprint, render_template, send_from_directory, request, redirect, url_for, flash
from pydantic import ValidationError

from src.database.models.game import GameAuth
from src.utils import static_folder
from src.main import user_controller

profile_route = Blueprint('profile', __name__)


@profile_route.get('/dashboard/profile')
async def get_profile():
    context = {}

    data = await user_controller.get_profile_by_game_id(game_id='3XZXLABF')
    context = dict(profile=data)
    return render_template('profile.html', **context)


@profile_route.get('/dashboard/settings')
async def get_settings():
    context = {}

    data = await user_controller.get_profile_by_game_id(game_id='3XZXLABF')
    context = dict(profile=data)
    return render_template('config.html', **context)


@profile_route.get('/dashboard/verification-request')
async def get_verification():
    context = {}
    return render_template('verification.html', **context)


@profile_route.post('/dashboard/verification-request')
async def do_verification():
    context = {}
    try:
        game_auth = GameAuth(**request.form)
    except ValidationError as e:
        pass

    flash(message="your account will be verified in 1 to 2 hours", category='success')
    return redirect(location=url_for('profile.get_settings'))


@profile_route.get('/dashboard/giftco')
async def get_gift_codes():
    context = {}
    return render_template('giftcodes.html', **context)


@profile_route.get('/dashboard/market-listing')
async def get_market_listing():
    context = {}
    return render_template('market_listing.html', **context)
