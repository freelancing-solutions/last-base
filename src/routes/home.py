from flask import Blueprint, render_template, send_from_directory
from src.utils import static_folder

home_route = Blueprint('home', __name__)


@home_route.get("/")
def get_home():
    context = {}
    return render_template('index.html', **context)


@home_route.get("/about")
def get_about():
    context = {}
    return render_template('about.html', **context)


@home_route.get("/faq")
def get_faq():
    context = {}
    return render_template('faq.html', **context)
