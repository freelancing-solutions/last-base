from flask import Blueprint, render_template, request, redirect, flash
from pydantic import ValidationError

from src.authentication import admin_login
from src.database.models.game import GiftCode
from src.database.models.users import User, UserUpdate
from src.main import user_controller, game_controller, email_service_controller

discord_route = Blueprint('discord', __name__)




@discord_route.get('/discord/channel')
async def get_discord_hook():
    """

    :return:
    """
    return render_template('discord/embed.html')


