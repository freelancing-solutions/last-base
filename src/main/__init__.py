from flask import Flask

from src.emailer import SendMail

send_mail = SendMail()
from src.controller.auth import UserController

user_controller = UserController()


def _add_blue_prints(app: Flask):
    """
        this function adds blueprints
    :param app:
    :return:
    """
    from src.routes.home import home_route
    from src.routes.auth import auth_route

    app.register_blueprint(home_route)
    app.register_blueprint(auth_route)


def _add_filters(app: Flask):
    """
        **add_filters**
            filters allows formatting from models to user readable format
    :param app:
    :return:
    """
    pass


def create_app(config):
    from src.utils import template_folder, static_folder
    app: Flask = Flask(__name__)
    app.template_folder = template_folder()
    app.static_folder = static_folder()
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['BASE_URL'] = "https://move-it.site"

    with app.app_context():
        _add_blue_prints(app)
        _add_filters(app)
        pass

    return app
