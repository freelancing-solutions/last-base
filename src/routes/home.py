from flask import Blueprint, render_template, send_from_directory

from src.authentication import user_details
from src.database.models.users import User
from src.utils import static_folder

home_route = Blueprint('home', __name__)


@home_route.get("/")
@user_details
async def get_home(user: User | None):
    context = {'user': user} if user else {}

    return render_template('index.html', **context)


@home_route.get("/about")
@user_details
async def get_about(user: User| None):
    context = {'user': user} if user else {}
    return render_template('about.html', **context)


@home_route.get("/faq")
@user_details
async def get_faq(user: User | None):
    context = {'user': user} if user else {}
    return render_template('faq.html', **context)
