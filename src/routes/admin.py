from flask import Blueprint, render_template, send_from_directory, request, redirect, url_for, flash
from pydantic import ValidationError

from src.authentication import login_required, admin_login
from src.database.models.game import GameAuth, GameIDS
from src.database.models.profile import ProfileUpdate
from src.database.models.users import User
from src.utils import static_folder
from src.main import user_controller, game_controller

admin_route = Blueprint('admin', __name__)


@admin_route.get('/admin')
@admin_login
async def get_admin(user: User):

    context = dict(user=user)
    return render_template('admin/admin.html', **context)


