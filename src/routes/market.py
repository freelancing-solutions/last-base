from flask import Blueprint, render_template, send_from_directory
from src.utils import static_folder

market_route = Blueprint('market', __name__)


@market_route.get('/dashboard/market/game_accounts')
def get_game_accounts():
    context = {}
    return render_template('market/accounts/game_accounts.html', **context)


@market_route.get('/dashboard/market/farm_accounts')
def get_farm_accounts():
    context = {}
    return render_template('market/farms/farms.html', **context)


@market_route.get('/dashboard/market/lss-skins')
def get_lss_skins():
    context = {}
    return render_template('market/skins/skins.html', **context)
