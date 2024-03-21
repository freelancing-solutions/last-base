from flask import Flask

from src.controller.encryptor import Encryptor
from src.emailer import SendMail
from src.utils import format_with_grouping

encryptor = Encryptor()
send_mail = SendMail()

from src.controller.auth import UserController
from src.controller.game_controller import GameController
from src.controller.market_controller import MarketController
from src.controller.wallet_controller import WalletController
from src.controller.paypal_controller import PayPalController

user_controller = UserController()
game_controller = GameController()
market_controller = MarketController()
wallet_controller = WalletController()
paypal_controller = PayPalController()

_controllers = [user_controller, game_controller, market_controller, wallet_controller, paypal_controller]


def _add_blue_prints(app: Flask):
    """
        this function adds blueprints
    :param app:
    :return:
    """
    from src.routes.home import home_route
    from src.routes.auth import auth_route
    from src.routes.market import market_route
    from src.routes.profile import profile_route
    from src.routes.admin import admin_route
    from src.routes.wallet import wallet_route
    from src.routes.email import email_route
    for route in [auth_route, home_route, profile_route, market_route, admin_route, wallet_route, email_route]:
        app.register_blueprint(route)


def _add_filters(app: Flask):
    """
        **add_filters**
            filters allows formatting from models to user readable format
    :param app:
    :return:
    """
    app.jinja_env.filters['number'] = format_with_grouping


def create_app(config):
    from src.utils import template_folder, static_folder
    app: Flask = Flask(__name__)
    app.template_folder = template_folder()
    app.static_folder = static_folder()
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['BASE_URL'] = "https://move-it.site"

    with app.app_context():
        from src.main.bootstrapping import bootstrapper
        bootstrapper()
        _add_blue_prints(app)
        _add_filters(app)
        encryptor.init_app(app=app)
        user_controller.init_app(app=app)
        game_controller.init_app(app=app)
        market_controller.init_app(app=app)
        wallet_controller.init_app(app=app)
        paypal_controller.init_app(app=app, config_instance=config)
        pass

    return app
