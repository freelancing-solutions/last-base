from flask import Flask

from src.controller.encryptor import Encryptor
from src.emailer import SendMail
from src.utils import format_with_grouping

encryptor = Encryptor()
send_mail = SendMail()
from src.controller.auth import UserController
from src.controller.game_controller import GameController

user_controller = UserController()
game_controller = GameController()


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

    app.register_blueprint(auth_route)
    app.register_blueprint(home_route)
    app.register_blueprint(profile_route)
    app.register_blueprint(market_route)
    app.register_blueprint(admin_route)


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
        pass

    return app
