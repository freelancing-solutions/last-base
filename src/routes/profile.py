from flask import Blueprint, render_template, send_from_directory, request, redirect, url_for, flash
from pydantic import ValidationError

from src.authentication import login_required
from src.database.models.game import GameAuth, GameIDS, GameDataInternal, GameAccountTypes
from src.database.models.market import SellerAccount, BuyerAccount
from src.database.models.profile import ProfileUpdate, Profile
from src.database.models.users import User, PayPal
from src.database.models.wallet import Wallet

from src.main import user_controller, game_controller, market_controller, wallet_controller, paypal_controller

profile_route = Blueprint('profile', __name__)


@profile_route.get('/dashboard/profile')
@login_required
async def get_profile(user: User):
    # TODO - there can be multiple profiles
    context = dict(user=user)
    profile: Profile = await user_controller.get_profile_by_uid(uid=user.uid)
    paypal_account: PayPal = await user_controller.get_paypal_account(uid=user.uid)
    wallet: Wallet = await wallet_controller.get_wallet(uid=user.uid)
    buyer_account: BuyerAccount = await market_controller.get_buyer_account(uid=user.uid)
    seller_account: SellerAccount = await market_controller.get_seller_account(uid=user.uid)

    if isinstance(paypal_account, PayPal):
        context.update(paypal_account=paypal_account)

    if isinstance(profile, Profile):
        context.update(profile=profile)
        print(f"Found Profile : {profile}")

    if isinstance(wallet, Wallet):
        context.update(wallet=wallet)

    if isinstance(seller_account, SellerAccount):
        context.update(seller_account=seller_account)
    if isinstance(buyer_account, BuyerAccount):
        context.update(buyer_account=buyer_account)

    return render_template('profile/profile.html', **context)


@profile_route.get('/dashboard/profile/game-accounts')
@login_required
async def get_accounts(user: User):
    context = dict(user=user)

    game_accounts: list[GameDataInternal] = await game_controller.get_game_accounts(uid=user.uid)
    print(game_accounts)
    total_accounts: int = len(game_accounts)
    context.update(game_accounts=game_accounts, GameAccountTypes=GameAccountTypes, total_accounts=total_accounts)
    return render_template('profile/game_accounts.html', **context)


@profile_route.get('/dashboard/edit-game/<string:game_id>')
@login_required
async def edit_base(user: User, game_id: str):
    context = dict(user=user)

    game_account: GameDataInternal | dict[str, str] = await game_controller.get_game_by_game_id(uid=user.uid,
                                                                                                game_id=game_id)

    context.update(game_account=game_account, game_account_types=GameAccountTypes)
    return render_template('profile/game_account.html', **context)


@profile_route.post('/dashboard/update-base')
@login_required
async def do_update_base(user: User):
    context = dict(user=user)
    game_id = request.form.get('game_id')
    account_type = request.form.get('account_type')

    game_account: GameDataInternal | dict[str, str] = await game_controller.update_game_account_type(game_id=game_id,
                                                                                                     account_type=account_type)

    context.update(game_account=game_account, game_account_types=GameAccountTypes)
    return render_template('profile/game_account.html', **context)


@profile_route.post('/dashboard/profile')
@login_required
async def update_profile(user: User):
    context = dict(user=user)
    try:

        updated_profile = ProfileUpdate(**request.form)
        print(f"Game Profile : {updated_profile}")
        updated_profile_: Profile = await user_controller.update_profile(updated_profile=updated_profile)
        if isinstance(updated_profile_, Profile):
            flash(message="profile updated", category="success")
        else:
            flash(message="Unable to Update Profile", category="danger")
    except ValidationError as e:
        flash(message=f"Error: {str(e)}", category="danger")

    return redirect(location=url_for('profile.get_profile'))


@profile_route.post('/dashboard/delete-profile')
@login_required
async def delete_profile(user: User):
    context = dict(user=user)
    try:

        game_id = request.form.get('main_game_id')
        print(f"Game ID: {game_id}")
        is_deleted = await user_controller.delete_profile(game_id=game_id)
        is_deleted_ = await game_controller.delete_game(game_id=game_id)
        # TODO consider deleting game listings on market
        if is_deleted and is_deleted_:
            flash(message="profile deleted", category="success")
        else:
            flash(message="cannot delete profile", category="danger")

    except ValidationError as e:
        flash(message=f"Error: {str(e)}", category="danger")

    return redirect(location=url_for('profile.get_profile'))


@profile_route.post('/dashboard/add-profile')
@login_required
async def add_game(user: User):
    game_id: str = request.form.get('game_id')
    profile = await user_controller.create_profile(main_game_id=game_id, uid=user.uid)
    game_ids = GameIDS(game_id_list=[profile.main_game_id])
    game_data = await game_controller.add_game_ids(uid=user.uid, game_ids=game_ids)
    flash(message="game profile created", category='success')
    return redirect(url_for('profile.get_profile'))


@profile_route.post('/dashboard/paypal')
@login_required
async def add_paypal(user: User):
    context = dict(user=user)
    try:
        paypal_email: str = request.form.get('paypal_account')
        become_seller: str = request.form.get('seller_account')
        become_buyer: str = request.form.get('buyer_account')
        print(f'Seller : {become_seller}')
    except ValidationError as e:
        _message: str = f"Error : str(e)"
        flash(message=_message, category='danger')
        return redirect(url_for('profile.get_profile'))

    data: PayPal = await user_controller.add_paypal(user=user, paypal_email=paypal_email)

    if not isinstance(data, PayPal):
        _message: str = "Unable to add paypal email to your account"
        flash(message=_message, category="danger")

        return redirect(location=url_for('profile.get_profile'))

    seller_account: SellerAccount = await market_controller.activate_seller_account(user=user, activate=True)
    buyer_account: BuyerAccount = await market_controller.activate_buyer_account(user=user, activate=True)

    _message: str = "Successfully created or updated your paypal account - please attach your account"
    flash(message=_message, category="success")

    return redirect(location=url_for('profile.get_profile'))


@profile_route.get('/dashboard/settings')
@login_required
async def get_settings(user: User):
    context = dict(user=user)

    profile: Profile = await user_controller.get_profile_by_uid(uid=user.uid)
    if profile:
        context.update(profile=profile)
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
    game_data_list = await game_controller.get_users_game_ids(uid=user.uid)
    active_gift_codes = await game_controller.get_active_gift_codes()
    total_bases: int = len(game_data_list)

    context = dict(user=user, total_bases=total_bases, game_data_list=game_data_list,
                   active_gift_codes=active_gift_codes)
    return render_template('gift_codes/gift_codes.html', **context)


@profile_route.post('/dashboard/gift-codes')
@login_required
async def add_game_ids(user: User):
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
                return redirect(url_for('profile.get_gift_codes'))

        game_ids = GameIDS(game_id_list=game_ids_list)
        completed = await game_controller.add_game_ids(uid=user.uid, game_ids=game_ids)

        if completed:
            flash("Successfully added game IDs. New codes will be automatically redeemed as they become available.",
                  "success")
        else:
            _message: str = "could not verify if game ids where added please try again"
            flash(message=_message, category="danger")

    except ValidationError as e:
        flash(f"Error: {str(e)}", "danger")

    return redirect(url_for('profile.get_gift_codes'))


@profile_route.get('/dashboard/market-listing')
@login_required
async def get_market_listing(user: User):
    context = dict(user=user)
    return render_template('market_listing.html', **context)


@profile_route.post('/dashboard/gift-codes-subscribe')
@login_required
async def gift_codes_subscribe(user: User):
    """

    :param user:
    :return:
    """
    subscription_amount: int = 30
    success_url: str = url_for('profile.gift_code_subscribe_success', _external=True)
    failure_url: str = url_for('profile.gift_code_subscribe_failure', _external=True)

    payment, is_created = await paypal_controller.create_payment(amount=subscription_amount, user=user,
                                                                 success_url=success_url, failure_url=failure_url)
    if is_created:
        # Redirect user to PayPal for payment approval
        for link in payment.links:
            if link.method == "REDIRECT":
                return redirect(link.href)
    else:
        flash(message=f"Error creating Payment : {payment.error}")
        return redirect(url_for('profile.get_profile'))

    _message = "Successfully Subscribed the Game ID's below to be automatically redeemed"

    flash(message=_message, category="danger")
    return redirect(url_for('profile.get_gift_codes'))


@profile_route.get('/dashboard/gift-codes-subscribe/success')
@login_required
async def gift_code_subscribe_success(user: User):
    pass


@profile_route.get('/dashboard/gift-codes-subscribe/failure')
@login_required
async def gift_code_subscribe_failure(user: User):
    pass
