from flask import Blueprint, render_template, send_from_directory

from src.authentication import login_required
from src.database.models.users import User
from src.utils import static_folder

market_route = Blueprint('market', __name__)


@market_route.get('/dashboard/market/game_accounts')
@login_required
async def get_game_accounts(user: User):
    context = {'user': user}
    return render_template('market/accounts/game_accounts.html', **context)


@market_route.get('/dashboard/market/farm_accounts')
@login_required
async def get_farm_accounts(user: User):
    context = {'user': user}
    return render_template('market/farms/farms.html', **context)


@market_route.get('/dashboard/market/lss-skins')
@login_required
async def get_lss_skins(user: User):
    context = {'user': user}
    return render_template('market/skins/skins.html', **context)
