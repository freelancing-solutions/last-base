import asyncio

from flask import Blueprint, render_template, send_from_directory, request, redirect, url_for, flash
from pydantic import ValidationError

from src.authentication import login_required, admin_login
from src.database.models.game import GameAuth, GameIDS, GiftCode
from src.database.models.profile import ProfileUpdate
from src.database.models.users import User, UserUpdate
from src.utils import static_folder
from src.main import user_controller, game_controller, email_service_controller

free_route = Blueprint('free', __name__)


@free_route.get('/free/gift-codes')
async def get_gift_codes():
    return render_template('free/gift_codes.html')


@free_route.post('/free/gift-codes/submit-game-id')
async def submit_game_id():
    try:
        game_ids = request.form.get('game_id')
        game_id_list = []

        # Splitting game IDs based on ',' or ';' and adding them to game_id_list
        if "," in game_ids:
            game_id_list = game_ids.split(",")
        elif ";" in game_ids:
            game_id_list = game_ids.split(";")
        else:
            game_id_list = [game_ids] if len(game_ids) == 8 else []

        # Ensure game_id_list does not exceed ten items
        if len(game_id_list) > 10:
            flash(message="Please provide a maximum of ten game ID's - or consider creating an account for a premium service", category="danger")
            return redirect(url_for('free.get_gift_codes'))

        if not game_id_list:
            flash(message="Please provide game ID's", category="danger")
            return redirect(url_for('free.get_gift_codes'))

        gift_codes = await game_controller.get_active_gift_codes()
        codes_list = [gift_code.code for gift_code in gift_codes if gift_code]
        print(codes_list)
        print(game_id_list)
        routines = []
        for game_id in game_id_list:
            for gift_code in codes_list:
                routines.append(game_controller.redeem_external(game_id=game_id, gift_code=gift_code))
        await asyncio.gather(*routines)

        mes = f"Completed code redemption - complete successfully - {len(game_ids)} Where gifted - Check your game Email"
        flash(message=mes, category="success")
        return redirect(url_for('free.get_gift_codes'))

    except Exception as e:
        print(str(e))
        flash(message="Completed code redemption - with possible errors", category="danger")
        return redirect(url_for('free.get_gift_codes'))

