from flask import Blueprint, render_template, send_from_directory
from src.utils import static_folder

profile_route = Blueprint('profile', __name__)


@profile_route.get('/dashboard/profile')
def get_profile():
    context = {}
    return render_template('profile.html', **context)
