from flask import Blueprint, render_template, send_from_directory, request, redirect, url_for, flash
from pydantic import ValidationError

from src.authentication import login_required, admin_login
from src.database.models.game import GameAuth, GameIDS, GiftCode
from src.database.models.profile import ProfileUpdate
from src.database.models.users import User
from src.utils import static_folder
from src.main import user_controller, game_controller

admin_route = Blueprint('admin', __name__)


@admin_route.get('/admin')
@admin_login
async def get_admin(user: User):
    context = dict(user=user)
    return render_template('admin/admin.html', **context)


@admin_route.get('/admin/gift-code')
@admin_login
async def get_gift_code(user: User):
    context = dict(user=user)
    return render_template('admin/gift_code.html', **context)


@admin_route.post('/admin/gift-code')
@admin_login
async def add_gift_code(user: User):
    """

    :param user:
    :return:
    """
    try:
        code: str = request.form.get('gift_code')
        number_days_valid: int = int(request.form.get('days_valid'))

        gift_code = GiftCode(code=code, number_days_valid=number_days_valid)
        gift_code_: GiftCode = await game_controller.add_new_gift_code(gift_code=gift_code)

        _mess: str = "Successfully added new gift code" if gift_code_ else "Unable to add Gift Code"
    except ValidationError as e:
        _mess: str = f"Error : {str(e)}"

    flash(message=_mess, category="success")
    context = dict(user=user)
    return render_template('admin/gift_code.html', **context)
