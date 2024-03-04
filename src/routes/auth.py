from flask import Blueprint, render_template, send_from_directory
from src.utils import static_folder

auth_route = Blueprint('auth', __name__)


@auth_route.get('/login')
def get_auth():
    context = {}
    return render_template('login.html', **context)




