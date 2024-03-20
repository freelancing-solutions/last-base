import json

from flask import Blueprint, render_template, send_from_directory, request, redirect, url_for, flash
from pydantic import ValidationError
from paypalrestsdk import Payment

from src.authentication import login_required
from src.database.models.game import GameAuth, GameIDS, GameDataInternal, GameAccountTypes
from src.database.models.market import SellerAccount, BuyerAccount
from src.database.models.profile import ProfileUpdate, Profile
from src.database.models.users import User, PayPal
from src.database.models.wallet import Wallet

from src.main import user_controller, game_controller, market_controller, wallet_controller, paypal_controller

wallet_route = Blueprint('wallet', __name__)


@wallet_route.post('/dashboard/wallet/deposit')
@login_required
async def make_deposit(user: User):
    """

    :param user:
    :return:
    """
    # Obtaining amount to deposit
    amount = request.form.get('deposit_amount')
    paypal = await user_controller.get_paypal_account(uid=user.uid)
    payment, is_created = await paypal_controller.create_payment(amount=amount, user=user, paypal=paypal)
    # Create payment

    if is_created:
        # Redirect user to PayPal for payment approval
        for link in payment.links:
            if link.method == "REDIRECT":
                return redirect(link.href)
    else:
        flash(message=f"Error creating Payment : {payment.error}")
        return redirect(url_for('profile.get_profile'))


@wallet_route.get('/dashboard/wallet/deposit-success')
@login_required
async def deposit_success(user: User):

    try:
        # Load JSON data
        _payload = request.json
        _signature = request.headers.get('Paypal-Transmission-Sig')
        request_valid = await paypal_controller.verify_signature(payload=_payload, signature=_signature)
        if not request_valid:
            redirect(url_for('home.get_home'))

        data = request.json

        # Extract payment amount
        amount = int(_payload.get("resource", {}).get("amount", {}).get("total"))

        wallet = await wallet_controller.get_wallet(uid=user.uid)
        transaction = await wallet.deposit_funds(amount=amount)
        transaction_saved = await wallet_controller.add_transaction(transaction=transaction)
        # Convert amount to float
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return None
    except Exception as e:
        print("An error occurred:", e)
        return None

    flash(message=f"Payment Of {amount} Made Successfully", category="success")
    return redirect(url_for('profile.get_profile'))


@wallet_route.get('/dashboard/wallet/deposit-failure')
@login_required
async def deposit_failure(user: User):

    flash(message=f"Please Note that you can make payment whenever you are ready", category="danger")
    return redirect(url_for('profile.get_profile'))
