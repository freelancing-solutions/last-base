from flask import Blueprint, render_template, send_from_directory, redirect, flash, url_for, request

from src.authentication import login_required
from src.database.models.users import User, PayPal
from src.main import paypal_controller, user_controller, market_controller
from src.utils import static_folder

market_route = Blueprint('market', __name__)


@market_route.get('/dashboard/market/request-approval')
@login_required
async def request_approval_to_sell(user: User):
    """
        this request will be made from the profile
    :param user:
    :return:
    """
    _approval_amount: int = 5
    paypal: PayPal = user_controller.get_paypal_account(uid=user.uid)
    success_url = url_for('market.approval_payment_success', _external=True)
    failure_url = url_for('market.approval_payment_failed', _external=True)
    payment, is_created = await paypal_controller.create_payment(amount=_approval_amount, user=user, paypal=paypal)
    if is_created:
        # Redirect user to PayPal for payment approval
        for link in payment.links:
            if link.method == "REDIRECT":
                return redirect(link.href)
    else:
        flash(message=f"Error creating Payment : {payment.error}")
        return redirect(url_for('profile.get_profile'))


@market_route.get('/dashboard/market/approval-success')
@login_required
async def approval_payment_success(user: User):
    """

    :param user:
    :return:
    """
    _payload = request.json
    _signature = request.headers.get('Paypal-Transmission-Sig')
    request_valid = await paypal_controller.verify_signature(payload=_payload, signature=_signature)
    if not request_valid:
        redirect(url_for('home.get_home'))

    amount = int(_payload.get("resource", {}).get("amount", {}).get("total"))
    if amount >= 5:
        account_approved: bool = await market_controller.approved_for_market(uid=user.uid, is_approved=True)
        if account_approved:
            flash(message="Your Account is successfully approved for selling accounts", category="success")
            return redirect(location=url_for('profile.get_profile'))

    _mes = "We are unable to approve your account for selling please contact us if you believe this is an error"
    flash(message=_mes, category="danger")
    return redirect(location=url_for('profile.get_profile'))


@market_route.post('/dashboard/market/approval-failed')
@login_required
async def approval_payment_failed(user: User):
    _mes = "We are unable to approve your account for selling please contact us if you believe this is an error"
    flash(message=_mes, category="danger")
    return redirect(location=url_for('profile.get_profile'))

@market_route.get('/dashboard/market/game_accounts')
@login_required
async def get_game_accounts(user: User):
    context = {'user': user}
    return render_template('market/accounts/game_accounts.html', **context)


@market_route.get('/dashboard/market/farm_accounts')
@login_required
async def get_farm_accounts(user: User):
    context = {'user': user}
    return render_template('market/farms/farms.html', **context)


@market_route.get('/dashboard/market/lss-skins')
@login_required
async def get_lss_skins(user: User):
    context = {'user': user}
    return render_template('market/skins/skins.html', **context)
