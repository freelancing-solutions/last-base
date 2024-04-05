import asyncio

from flask import Blueprint, render_template, send_from_directory, request, redirect, url_for, flash
from pydantic import ValidationError

from src.authentication import login_required, admin_login, user_details
from src.database.models.game import GameAuth, GameIDS, GiftCode
from src.database.models.profile import ProfileUpdate
from src.database.models.users import User, UserUpdate
from src.utils import static_folder
from src.main import user_controller, game_controller, email_service_controller

free_route = Blueprint('free', __name__)


@free_route.get('/free/gift-codes')
@user_details
async def get_gift_codes(user: User):
    social_url = url_for('free.get_gift_codes', _external=True)
    context = dict(user=user, social_url=social_url)
    return render_template('free/gift_codes.html', **context)


@free_route.post('/free/gift-codes/submit-game-id')
async def submit_game_id():
    try:
        game_ids = request.form.get('game_id')
        game_ids = game_ids.strip().upper()
        if not game_ids:
            flash(message="Please provide game ID's", category="danger")
            return redirect(url_for('free.get_gift_codes'))

        # Split game IDs based on delimiters and filter out empty strings
        delimiters = [",", ";", ".", " "]
        game_id_list = []
        for delimiter in delimiters:
            for game_id in game_ids.split(delimiter):
                if game_id:
                    game_id_list.append(game_id)
            break

        if len(game_id_list) > 50:
            flash(message="Please provide a maximum of 50 game ID's - or consider creating an account for a premium "
                          "service", category="danger")
            return redirect(url_for('free.get_gift_codes'))

        game_ids_base = GameIDS(game_id_list=game_id_list)

        store_game_ids = await game_controller.add_game_ids(game_ids=game_ids_base, uid="11111111")

        gift_codes = await game_controller.get_active_gift_codes()
        codes_list = [gift_code.code for gift_code in gift_codes if gift_code]
        routines = [game_controller.redeem_external(game_id=game_id, gift_code=gift_code) for game_id in game_id_list for gift_code in codes_list]

        results = await asyncio.gather(*routines)

        mes = (f"Completed code redemption - complete successfully - {len(game_id_list)} Accounts Where gifted - Check "
               f"your game Email")

        context = dict(results=results)
        flash(message=mes, category="success")
        return render_template('free/gift_codes.html', **context)

    except Exception as e:
        flash(message=f"An error occurred: {str(e)}", category="danger")
        return redirect(url_for('free.get_gift_codes'))

