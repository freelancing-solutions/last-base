from flask import Flask, url_for
from paypalrestsdk import configure, Api, Payment
from src.config import Settings
from src.controller import Controllers
from src.database.models.users import User, PayPal


class PayPalController(Controllers):
    def __init__(self):
        super().__init__()
        self.mode = "sandbox"


    def init_app(self, app: Flask, config_instance: Settings):
        configure({
            "mode": self.mode,
            "client_id": config_instance.PAYPAL_SETTINGS.CLIENT_ID,
            "client_secret": config_instance.PAYPAL_SETTINGS.SECRET_KEY
        })
        # self.api = Api(**{
        #     "mode": self.mode,
        #     "client_id": config_instance.PAYPAL_SETTINGS.CLIENT_ID,
        #     "client_secret": config_instance.PAYPAL_SETTINGS.SECRET_KEY
        # })
        super().init_app(app=app)

    async def create_payment(self, amount: int, user: User, paypal: PayPal) -> tuple[Payment, bool]:
        """
        :param paypal:
        :param user:
        :param amount: The amount of the payment
        :param customer_info: Information about the customer
        :param uid: User ID to be included
        :return: A tuple containing the Payment object and a boolean indicating success or failure
        """
        _deposit_success_url = url_for('wallet.deposit_success')
        _deposit_failed_url = url_for('wallet.deposit_failure')

        # Include customer information and UID
        payment = Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": _deposit_success_url,
                "cancel_url": _deposit_failed_url
            },
            "transactions": [{
                "amount": {
                    "total": amount,
                    "currency": "USD"
                },
                "description": f"Deposit to wallet : {user.uid}"
            }],
        })

        return payment, payment.create()
