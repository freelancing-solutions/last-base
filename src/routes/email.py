from flask import Blueprint, render_template, send_from_directory, request, redirect, url_for, flash
from pydantic import ValidationError

from src.authentication import login_required, admin_login
from src.database.models.email_service import EmailService
from src.database.models.game import GameAuth, GameIDS, GiftCode
from src.database.models.profile import ProfileUpdate
from src.database.models.users import User, PayPal
from src.utils import static_folder
from src.main import user_controller, game_controller, paypal_controller, email_service_controller

email_route = Blueprint('email', __name__)


@email_route.get('/dashboard/email')
@login_required
async def get_email(user: User):
    context = dict(user=user)
    return render_template('email/email_service.html', **context)


@email_route.post('/dashboard/email/email-subscribe')
@login_required
async def create_subscription(user: User):
    try:
        # Extract data from the form
        email = request.form.get('email')
        subscription_term = int(request.form.get('subscription_term'))
        total_emails = int(request.form.get('total_emails'))
        email_service = EmailService(uid=user.uid, email=email, subscription_term=subscription_term,
                                     total_emails=total_emails)
        paypal: PayPal = user_controller.get_paypal_account(uid=user.uid)
        print(email_service)
        print(email_service.total_amount)
        success_url: str = url_for('email.subscription_success', _external=True)
        failure_url: str = url_for('email.subscription_failed', _external=True)

        payment, is_created = await paypal_controller.create_payment(amount=email_service.total_amount, user=user,
                                                                     paypal=paypal, success_url=success_url,
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
        return redirect(location=url_for('email.get_email'))


@email_route.get('/dashboard/email/subsciption-success')
@login_required
async def subscription_success(user: User):
    _payload = request.json
    _signature = request.headers.get('Paypal-Transmission-Sig')
    request_valid = await paypal_controller.verify_signature(payload=_payload, signature=_signature)
    if not request_valid:
        redirect(url_for('home.get_home'))
    is_active = email_service_controller.activation_email_service(user=user, activate=True)
    if is_active:
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
