from flask import Blueprint, render_template, send_from_directory, request, redirect, url_for, flash
from pydantic import ValidationError

from src.authentication import login_required, admin_login
from src.database.models.game import GameAuth, GameIDS, GiftCode
from src.database.models.profile import ProfileUpdate
from src.database.models.users import User, UserUpdate
from src.utils import static_folder
from src.main import user_controller, game_controller, email_service_controller

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
    gift_codes: list[GiftCode] = await game_controller.get_all_gift_codes()
    context = dict(user=user, gift_codes=gift_codes)
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


@admin_route.get('/admin/email-service')
@admin_login
async def get_email_service(user: User):
    try:
        context = dict(user=user)
        email_services = await email_service_controller.get_all_active_subscriptions()
        context.update(email_services=email_services)
        return render_template('admin/email_service.html', **context)
    except Exception:
        pass


@admin_route.get('/admin/accounts')
@admin_login
async def get_accounts(user: User):
    try:
        context = dict(user=user)
        accounts_list = await user_controller.get_all_accounts()

        context.update(accounts_list=accounts_list, total_accounts=len(accounts_list))
        return render_template('admin/accounts.html', **context)
    except Exception as e:
        context = dict(user=user, accounts_list=[], total_accounts=0)
        print(str(e))
        flash(message=str(e), category="danger")
        return render_template('admin/accounts.html', **context)


@admin_route.get('/admin/account/<string:uid>')
@admin_login
async def edit_user(user: User, uid: str):
    try:
        account = await user_controller.get_account_by_uid(uid=uid)
        if account:
            context = dict(user=user, account=account)
            return render_template('admin/edit_account.html', **context)
    except Exception as e:
        context = dict(user=user)
        print(str(e))
        flash(message=str(e), category="danger")
        return render_template('admin/accounts.html', **context)


@admin_route.post('/admin/account/<string:uid>')
@admin_login
async def update_account(user: User, uid: str):
    try:
        account_update = UserUpdate(**request.form)
        # will update account
    except ValidationError as e:
        print(str(e))
        flash(message=str(e), category='danger')
        return redirect('admin.get_accounts')
