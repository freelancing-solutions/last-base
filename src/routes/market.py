from flask import Blueprint, render_template, send_from_directory, redirect, flash, url_for, request
from pydantic import ValidationError

from src.authentication import login_required, user_details
from src.database.models.game import GameDataInternal
from src.database.models.market import SellerAccount, BuyerAccount, MainAccountsCredentials, MarketMainAccounts
from src.database.models.users import User, PayPal
from src.main import paypal_controller, user_controller, market_controller, game_controller
from src.utils import static_folder

market_route = Blueprint('market', __name__)




@market_route.get('/dashboard/market/listing-accounts')
@login_required
async def get_how_to(user: User):
    context = dict(user=user)
    return render_template('market/how_to.html', **context)

@market_route.get('/dashboard/market/request-approval')
@login_required
async def request_approval_to_sell(user: User):
    """
        this request will be made from the profile
    :param user:
    :return:
    """
    _approval_amount: int = 5
    paypal: PayPal = await user_controller.get_paypal_account(uid=user.uid)
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
        seller_account = await market_controller.get_seller_account(uid=user.uid)
        buyer_account = await market_controller.get_buyer_account(uid=user.uid)
        context.update(seller_account=seller_account)
        context.update(buyer_account=buyer_account)
        return render_template('market/accounts/tabs/my_dashboard.html', **context)
    except Exception as e:
        pass


@market_route.get('/dashboard/market/listings')
@user_details
async def get_public_market(user: User):
    try:
        context = {'user': user}
        listed_accounts = await market_controller.get_public_listed_accounts()
        social_url = url_for('market.get_public_market', _external=True)
        context = dict(user=user, social_url=social_url, listed_accounts=listed_accounts)

        return render_template('market/accounts/tabs/public_listings.html', **context)
    except Exception as e:
        flash(message="Error tryubg to access public market - please try again later", category="danger")
        return redirect('main.get_home')


@market_route.get('/dashboard/market/listing/<string:listing_id>')
@user_details
async def get_public_listing(user: User, listing_id: str):
    """

    :param user:
    :param listing_id:
    :return:
    """
    try:
        context = dict(user=user)
        listed_account = await market_controller.get_listed_account(listing_id=listing_id)
        if not listed_account:
            flash(message="Unable to obtain listed account, please try again later", category="danger")
            return redirect(url_for('market.get_account_trader_dashboard'))
        social_url = url_for('market.get_public_listing', _external=True)
        context = dict(user=user, social_url=social_url, listed_account=listed_account)
        return render_template('market/accounts/tabs/dashboard_tabs/listed_account_details.html', **context)
    except Exception as e:
        print(str(e))
        flash(message="Unable to obtain listed account details please report this error", category="danger")
        return redirect(url_for('market.get_account_trader_dashboard'))


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
            flash(message="You are not Authorized to Sell in our Market Place - please Verify your Account then "
                          "Continue with your Listing, You can verify your Account by Activating your Merchant "
                          "Account Below", category="danger")

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
            flash(message="Unable to create a listing please inform us of this error so we may help resolve it",
                  category="danger")
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
        if not (listed_account.uid == user.uid):
            flash(message="You are not authorized to view or edit this listing", category='danger')
            return redirect(url_for('market.get_account_trader_dashboard'))

        context = dict(user=user, listing=listed_account)
        return render_template('market/accounts/tabs/dashboard_tabs/listing_editor.html', **context)

    except Exception as e:
        print(str(e))
        flash(message="There was an error trying to fetch account listing - please inform admin", category="danger")
        return redirect('market.get_account_trader_dashboard')


@market_route.post('/dashboard/market/update-listed-account')
@login_required
async def do_update_listing(user: User):
    # Extract form data from the request
    form_data = request.form

    # Retrieve listing information
    listing_id = form_data.get('listing_id')
    total_gold_cards = int(form_data.get('total_gold_cards'))
    total_hero_tokens = int(form_data.get('total_hero_tokens'))
    total_skins = int(form_data.get('total_skins'))
    gold_sets_vehicles = int(form_data.get('gold_sets_vehicles'))
    gold_sets_fighters = int(form_data.get('gold_sets_fighters'))
    gold_sets_shooters = int(form_data.get('gold_sets_shooters'))
    bane_blade_sets = int(form_data.get('bane_blade_sets'))
    fighter_units_level = int(form_data.get('fighter_units_level'))
    shooter_units_level = int(form_data.get('shooter_units_level'))
    vehicle_units_level = int(form_data.get('vehicle_units_level'))
    state_season = int(form_data.get('state_season'))
    season_heroes = int(form_data.get('season_heroes'))
    sp_heroes = int(form_data.get('sp_heroes'))
    universal_sp_medals = int(form_data.get('universal_sp_medals'))
    amount_spent_packages = int(form_data.get('amount_spent_packages'))
    vip_shop = form_data.get('vip_shop') == 'on'  # Convert checkbox value to boolean
    energy_lab_level = int(form_data.get('energy_lab_level'))
    energy_lab_password = form_data.get('energy_lab_password')

    listed_account = await market_controller.get_listed_account_by_listing_id(listing_id=listing_id)
    if isinstance(listed_account, MarketMainAccounts):
        listed_account.uid = user.uid
        listed_account.total_gold_cards = total_gold_cards
        listed_account.total_hero_tokens = total_hero_tokens
        listed_account.total_skins = total_skins
        listed_account.gold_sets_vehicles = gold_sets_vehicles
        listed_account.gold_sets_fighters = gold_sets_fighters
        listed_account.gold_sets_shooters = gold_sets_shooters
        listed_account.bane_blade_sets = bane_blade_sets
        listed_account.fighter_units_level = fighter_units_level
        listed_account.shooter_units_level = shooter_units_level
        listed_account.vehicle_units_level = vehicle_units_level
        listed_account.state_season = state_season
        listed_account.season_heroes = season_heroes
        listed_account.sp_heroes = sp_heroes
        listed_account.universal_sp_medals = universal_sp_medals
        listed_account.amount_spent_packages = amount_spent_packages
        listed_account.vip_shop = vip_shop
        listed_account.energy_lab_level = energy_lab_level
        listed_account.energy_lab_password = energy_lab_password
        listed_account.listing_active = True
        listed_account.in_negotiation = False
        listed_account.is_bought = False

        listed_account_ = await market_controller.update_listed_account(listed_account)
        if listed_account_:
            flash(message="Successfully updated listed account", category="success")
            return redirect(url_for('market.list_game_account'))

        flash(message="Error listing your account please try again later if problem persists inform admin", category="danger")
        return redirect(url_for('market.list_game_account'))
