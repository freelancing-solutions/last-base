from flask import Blueprint, render_template, send_file, jsonify, url_for, flash, redirect
from datetime import datetime, timedelta
from src.authentication import user_details
from src.database.models.users import User
from src.main import game_controller
from src.utils import static_folder

home_route = Blueprint('home', __name__)


@home_route.get('/get-time')
async def get_time():
    # Get the current server time
    current_time = datetime.utcnow()

    # Convert the datetime object to a string
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")

    # Return the current time as a JSON response
    return jsonify({'time': current_time_str})


@home_route.get('/game-hourly')
async def get_game_hourly_event():
    hourly_event: str = await game_controller.get_hourly_event()
    hourly_event = hourly_event.upper()
    data = {'event': hourly_event}
    return jsonify(data)


@home_route.get('/game-time')
async def game_time():
    # Get the current server time in UTC
    current_time_utc = datetime.utcnow()

    # Convert the datetime object to a string
    current_time_str = (current_time_utc - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S.%f")

    # Return the current time as a JSON response
    return jsonify({'time': current_time_str})


@home_route.get("/")
@user_details
async def get_home(user: User | None):

    social_url = url_for('home.get_home', _external=True)
    context = dict(user=user, social_url=social_url)
    return render_template('index.html', **context)


@home_route.get("/about")
@user_details
async def get_about(user: User | None):
    social_url = url_for('home.get_about', _external=True)
    context = {'user': user, 'social_url': social_url} if user else {'social_url': social_url}
    return render_template('about.html', **context)


@home_route.get("/faq")
@user_details
async def get_faq(user: User | None):

    social_url = url_for('home.get_faq', _external=True)
    context = dict(user=user, social_url=social_url)
    return render_template('faq.html', **context)


@home_route.get("/downloads")
@user_details
async def get_downloads(user: User | None):
    context = {'user': user} if user else {}
    social_url = url_for('home.get_downloads', _external=True)
    context = dict(user=user, social_url=social_url)
    context = dict(user=user, social_url=social_url)

    return render_template('downloads.html', **context)


@home_route.get("/downloads/android/latest-version")
@user_details
async def download_latest_version(user: User | None):
    """
        assume the apk file to be downloaded is located in static folder
        under the name latest.apk
    :param user:
    :return:
    """
    try:
        apk_file_path = f"{static_folder()}/downloads/latest.apk"
        return send_file(apk_file_path, as_attachment=True)
    except Exception as e:
        return f"Failed to download Android APK Last Shelter Survival: ()", 500


@home_route.get("/downloads/android/previous-version")
@user_details
async def download_previous_version(user: User | None):
    """
        assume the apk file to be downloaded is located in static folder
        under the name latest.apk
    :param user:
    :return:
    """
    try:
        apk_file_path = f"{static_folder()}/downloads/previous.apk"
        return send_file(apk_file_path, as_attachment=True)
    except Exception as e:
        return f"Failed to download Android APK Last Shelter Survival: ()", 500


@home_route.get("/how-last-shelter-works")
@user_details
async def get_how(user: User):
    """

    :param user:
    :return:
    """

    try:
        context = {'user': user} if user else {}
        return render_template('how.html', **context)
    except Exception as e:
        print(str(e))
        flash("Error accessing how things work try again later", category="danger")
        return redirect(url_for('home.get_home'))

