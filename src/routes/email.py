import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

from src.authentication import login_required
from src.config import config_instance
from src.database.models.email_service import EmailService, EmailSubscriptions
from src.database.models.users import User, PayPal
from src.main import user_controller, paypal_controller, email_service_controller

email_route = Blueprint('email', __name__)


@email_route.get('/dashboard/email')
@login_required
async def get_email(user: User):
    context = dict(user=user)
    email_service: EmailService = await email_service_controller.get_email_service(user=user)
    email_subscription_list: list[EmailSubscriptions] = await email_service_controller.get_email_service_subscription(
        subscription_id=email_service.subscription_id)

    if email_service and email_service.subscription_active and not email_service.subscription_running:
        context.update(email_service=email_service)
        return render_template('email/subscription.html', **context)

    if email_service and email_service.subscription_active and email_service.subscription_running:
        context.update(email_service=email_service, email_subscription_list=email_subscription_list)
        return render_template('email/active.html', **context)

    return render_template('email/email_service.html', **context)


@email_route.post('/dashboard/email/email-subscribe')
@login_required
async def create_subscription(user: User):
    try:
        # Extract data from the form
        email = request.form.get('email')
        email = email.strip().lower()
        email_stub = request.form.get('email_stub')
        email_stub = email_stub.strip().lower()
        subscription_term = int(request.form.get('subscription_term'))
        total_emails = int(request.form.get('total_emails'))

        stub_exist = await email_service_controller.email_stub_exist(email_stub=email_stub)
        if stub_exist:
            flash(message="Email Stub Already used please pick another", category="danger")
            return redirect(location=url_for('email.get_email'))

        email_service = EmailService(uid=user.uid, email=email, email_stub=email_stub,
                                     subscription_term=subscription_term,
                                     total_emails=total_emails)

        paypal: PayPal = await user_controller.get_paypal_account(uid=user.uid)
        print(email_service)
        print(email_service.total_amount)
        success_url: str = url_for('email.subscription_success', _external=True)
        failure_url: str = url_for('email.subscription_failed', _external=True)

        payment, is_created = await paypal_controller.create_payment(amount=email_service.total_amount,
                                                                     user=user,
                                                                     paypal=paypal,
                                                                     success_url=success_url,
                                                                     failure_url=failure_url)
        if is_created:
            # Redirect user to PayPal for payment approval
            email_service = await email_service_controller.create_email_subscription(email_service=email_service)
            for link in payment.links:
                if link.method == "REDIRECT":
                    return redirect(link.href)
        else:
            flash(message=f"Error Subscribing to our email service : {payment.error}")

        return redirect(location=url_for('email.get_email'))
    except Exception as e:
        # Handle exceptions appropriately, like logging the error
        print("An error occurred:", e)
        message = str(e)
        flash(message=message, category='danger')
        return redirect(location=url_for('email.get_email'))


@email_route.get('/dashboard/email/subsciption-success')
@login_required
async def subscription_success(user: User):
    _payload = request.json
    _signature = request.headers.get('Paypal-Transmission-Sig')
    request_valid = await paypal_controller.verify_signature(payload=_payload, signature=_signature)
    if not request_valid:
        redirect(url_for('home.get_home'))
    email_service = await email_service_controller.activation_email_service(user=user, activate=True)
    if isinstance(email_service, EmailService):
        email_addresses = await email_service_controller.create_email_addresses(email_service=email_service)
        _mess: str = "Your Email Service has been activated - please start using the service ASAP"
        flash(message=_mess, category="success")
    else:
        # TODO - do something about this error here,
        _mess: str = f"Error Code: 303, Unable to activate service please inform us"
        flash(message=_mess, category="danger")

    return redirect(location=url_for('email.get_email'))


@email_route.get('/dashboard/email/subscription-failed')
@login_required
async def subscription_failed(user: User):
    _mess: str = "There was a Problem activating your Email Service if you think this is an Error please contact us"
    flash(message=_mess, category="danger")
    return redirect(location=url_for('email.get_email'))


@email_route.get('/dashboard/email/dashboard')
@login_required
async def email_service_dashboard(user: User):
    pass


@email_route.get('/_handlers/email-service/account-verification')
async def link_processor():
    """
        The Authentication for this route should be custom
    :return:
    """
    try:
        auth_token: str = request.headers.get('Auth')
        if auth_token != config_instance().CLOUDFLARE_SETTINGS.X_CLIENT_SECRET_TOKEN:
            return "Not Found", 404

        body = request.json
        link = body.get('link')
        # This is the email of the client it was used to activate a game account at this point
        email = body.get('email')
        email_used = await email_service_controller.email_used(email=email)
        if email_used:
            return requests.get(link)
        else:
            return "Unknown Address"

    except Exception as e:
        print(str(e))
        return "Error - See logs", 500


@email_route.get('/_handlers/email-service/email-maps')
async def email_mappings():
    """
        Must return a map containing all email pairs to be mapped by cloudflare
    """
    auth_token: str = request.headers.get('Auth')
    if auth_token != config_instance().CLOUDFLARE_SETTINGS.X_CLIENT_SECRET_TOKEN:
        return "Not Found", 404

    email_maps = await email_service_controller.return_mappings()

    return jsonify(email_maps)


@email_route.get('/_handlers/email-service/map/<string:email>')
async def map_email(email: str):
    """
        TODO caching the results of this endpoint is highly important
    :param email:
    :return:
    """
    auth_token: str = request.headers.get('Auth')
    print(auth_token)
    if auth_token != config_instance().CLOUDFLARE_SETTINGS.X_CLIENT_SECRET_TOKEN:
        return "Not Found", 404

    map_to = await email_service_controller.map_to(email=email)
    if map_to:
        results = {
            'map_to': map_to
        }
    else:
        results = {
            'map_to': "noreply@last-shelter.vip"
        }
    return results
