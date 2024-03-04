from flask import Blueprint, render_template, send_from_directory
from src.utils import static_folder
from src.main import user_controller
profile_route = Blueprint('profile', __name__)


@profile_route.get('/dashboard/profile')
async def get_profile():
    context = {}

    data = await user_controller.get_profile_by_game_id(game_id='3XZXLABF')
    context = dict(profile=data)
    return render_template('profile.html', **context)
