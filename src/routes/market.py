from flask import Blueprint, render_template, send_from_directory, redirect, flash, url_for, request
from pydantic import ValidationError

from src.authentication import login_required, user_details
from src.database.models.game import GameDataInternal
from src.database.models.market import SellerAccount, BuyerAccount, MainAccountsCredentials, MarketMainAccounts
from src.database.models.users import User, PayPal
from src.main import paypal_controller, user_controller, market_controller, game_controller
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
    payment, is_created = await paypal_controller.create_payment(amount=_approval_amount,
                                                                 user=user,
                                                                 paypal=paypal,
                                                                 success_url=success_url, failure_url=failure_url)
    if is_created:
        # Redirect user to PayPal for payment approval
        seller_account: SellerAccount = await market_controller.activate_seller_account(user=user, activate=True)
        buyer_account: BuyerAccount = await market_controller.activate_buyer_account(user=user, activate=True)

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


@market_route.get('/dashboard/market/approval-failed')
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


@market_route.get('/dashboard/market/trader-dashboard')
@login_required
async def get_account_trader_dashboard(user: User):
    try:
        context = {'user': user}
        return render_template('market/accounts/tabs/my_dashboard.html', **context)
    except Exception as e:
        pass


@market_route.get('/dashboard/market/listings')
@user_details
async def get_public_market(user: User):
    try:
        context = {'user': user}
        return render_template('market/accounts/tabs/public_listings.html', **context)
    except Exception as e:
        pass


@market_route.post('/dashboard/market/list-game-account')
@login_required
async def list_game_account(user: User):
    """
        will verify manage and start a game account listing
    :param user:
    :return:
    """
    try:
        context = {'user': user}
        game_id = request.form.get('game_id')
        price = request.form.get('price')
        email = request.form.get('email')
        password = request.form.get('password')
        pin = request.form.get('pin')

        # Obtain a record of the seller
        seller_account = await market_controller.get_seller_account(uid=user.uid)

        if not (seller_account.account_activated and seller_account.account_verified):
            flash(message="You are not verified to sell in our market place - please verify your account then "
                          "continue with your listing", category="danger")
            return redirect(url_for('profile.get_profile'))

        # Check the Seller rating if it's lower than 3 then indicate to seller that rating is too low
        # and allow him to improve the rating
        if seller_account.seller_rating < 3:
            flash(message="Seller Rating too low - please improve your seller rating", category="danger")
            return redirect(url_for('market.get_account_trader_dashboard'))

        # creating account credentials record
        main_account_credentials = MainAccountsCredentials(game_id=game_id,
                                                           account_email=email,
                                                           account_password=password,
                                                           account_pin=pin)
        # print(game_id, price, email, password, pin)
        is_account_valid = await game_controller.game_account_valid(email=main_account_credentials.account_email,
                                                                    password=main_account_credentials.account_password)
        print("Game Account Valid: ", is_account_valid)

        # checking if account is valid, if not inform user then exit
        if not is_account_valid:
            # TODO consider subtracting seller rating on multiple submissions - which are negative
            # TODO also subtract seller rating for every listing that is bogus

            flash(message="Your Game Login Details are invalid", category="danger")
            return redirect(url_for('market.get_game_accounts'))

        # This will mean that accounts must first be listed in the owner profile before they can be sold
        game_data = await game_controller.get_game_by_game_id(uid=user.uid, game_id=main_account_credentials.game_id)
        if not isinstance(game_data, GameDataInternal):
            flash(message="Please Ensure to claim your account in your profile before you can list it for sale",
                  category="danger")
            return redirect(url_for('profile.get_profile'))

        print(f"Game Data : {game_data.dict()}")

        main_account_credentials.is_verified = True

        # Starting by adding the credentials
        game_account_credentials = await market_controller.add_game_account_credentials(
            game_account=main_account_credentials)
        if not isinstance(game_account_credentials, MainAccountsCredentials):
            flash(message="This account has already being listed for sale- if you believe this is a mistake please "
                          "let us know", category="danger")

            return redirect(url_for('market.get_game_accounts'))

        market_account = MarketMainAccounts(uid=user.uid, game_id=game_data.game_id, game_uid=game_data.game_uid,
                                            state=game_data.state, base_level=game_data.base_level,
                                            base_name=game_data.base_name, item_price=price)

        account_listing = await market_controller.add_account_market_listing(market_account=market_account,
                                                                             account_credentials=main_account_credentials)
        if not account_listing:
            flash(message="Unable to create a listing please inform us of this error so we may help resolve it", category="danger")
            return redirect(url_for('market.get_account_listings'))

        flash(message="Successfully submitted Game Account for listing", category="success")
        return redirect(url_for('market.get_game_accounts'))

    except ValidationError as e:
        print(str(e))
        flash(message="Please Provide Minimum Game Credentials Needed to Login", category="success")
        return redirect(url_for('market.get_game_accounts'))


@market_route.post('/dashboard/market/listed-account/<string:listing_id>')
@login_required
async def get_listing_editor(user: User, listing_id: str):
    """

    :param listing_id:
    :param user:
    :return:
    """
    try:
        listed_account = await market_controller.get_listed_account(listing_id=listing_id)

        # Verifying if the person requesting the account actually owns the account listing
        if not(listed_account.uid == user.uid):
            flash(message="You are not authorized to view or edit this listing", category='danger')
            return redirect(url_for('market.get_account_trader_dashboard'))

        context = dict(user=user, listing=listed_account)
        return render_template('market/accounts/tabs/dashboard_tabs/listing_editor.html', **context)
    except Exception as e:
        print(str(e))
        flash(message="there was an error trying to fetch account listing - please inform admin", category="danger")
        return redirect('market.get_account_trader_dashboard')