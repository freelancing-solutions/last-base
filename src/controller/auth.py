import time
import uuid

from flask import Flask, render_template
from pydantic import ValidationError
from sqlalchemy import or_

from src.controller import error_handler, UnauthorizedError, Controllers
from src.database.models.profile import Profile, ProfileUpdate
from src.database.models.users import User, CreateUser, UserUpdate
from src.database.sql.user import UserORM, ProfileORM
from src.emailer import EmailModel
from src.main import send_mail
import requests


class UserController(Controllers):

    def __init__(self):
        super().__init__()

        self._time_limit = 360
        self._verification_tokens: dict[str, int | dict[str, str | int]] = {}
        self.profiles: dict[str, Profile] = {}
        self.users: dict[str, User] = {}
        self._game_data_url: str = 'https://gslls.im30app.com/gameservice/web_getserverbyname.php'

    def init_app(self, app: Flask):
        super().init_app(app=app)

    async def _get_game_data(self, game_id: str, lang: str = 'en') -> dict[str, str | int]:
        """

        :param game_id:
        :param lang:
        :return:
        """
        _params = {'name': game_id, 'lang': lang}
        response = requests.get(url=self._game_data_url, params=_params)
        game_data = response.json()
        print("Game Data 1")
        print(game_data)
        return game_data

    async def manage_users_dict(self, new_user: User):
        # Check if the user instance already exists in the dictionary
        self.users[new_user.game_id] = new_user

    async def manage_profiles(self, new_profile: Profile):
        self.profiles[new_profile.game_id] = new_profile

    async def get_profile_by_game_id(self, game_id: str) -> Profile | None:
        """
        Get the profile for the given user ID.

        :param game_id: The user ID for which to retrieve the profile.
        :return: The Profile instance corresponding to the user ID if found, else None.
        """
        # Check if the profile is available in the cache (profiles dictionary)
        if game_id in self.profiles:
            self.logger.info("Fetching profile from dict {} ")
            return self.profiles.get(game_id)

        # Fetch the profile data from the database
        with self.get_session() as session:
            profile_orm = session.query(ProfileORM).filter(ProfileORM.game_id == game_id).first()
            # If the profile_orm is not found, return None
            if not profile_orm:
                game_data = await self._get_game_data(game_id=game_id)
                profile = Profile(**game_data, game_id=game_id)
                profile_orm = ProfileORM(**profile.dict())
                session.add(profile_orm)
                session.commit()
            else:
                # Convert ProfileORM to Profile object
                profile = Profile(**profile_orm.to_dict())

            # Cache the profile in the dictionary for future use
            self.profiles[game_id] = profile
        return profile

    async def update_profile(self, updated_profile: ProfileUpdate) -> Profile | None:
        """

        :param updated_profile:
        :return:
        """
        with self.get_session() as session:
            original_profile: ProfileORM = session.query(ProfileORM).filter(ProfileORM.game_id == updated_profile.game_id).first()
            print(original_profile.to_dict())
            if isinstance(original_profile, ProfileORM):
                original_profile.alliancename = updated_profile.alliancename
                original_profile.allianceabr = updated_profile.allianceabr
                session.merge(original_profile)
                profile = Profile(**original_profile.to_dict())
                session.commit()
                return profile
            return {}

    async def is_token_valid(self, token: str) -> bool:
        """
        **is_token_valid**
            Checks if the password reset token is valid based on the elapsed time.
        :param token: The password reset token to validate.
        :return: True if the token is valid, False otherwise.
        """
        if token in set(self._verification_tokens.keys()):
            timestamp: int = self._verification_tokens[token]
            current_time: int = int(time.time())
            elapsed_time = current_time - timestamp
            return elapsed_time < self._time_limit

        return False

    @error_handler
    async def get(self, game_id: str) -> dict[str, str] | None:
        """
        :param game_id:
        :return:
        """
        if not game_id:
            return None
        if game_id in self.users:
            return self.users[game_id].dict()

        with self.get_session() as session:
            user_data: UserORM = session.query(UserORM).filter(UserORM.game_id == game_id).first()
            return user_data.to_dict()

    @error_handler
    async def get_by_email(self, email: str) -> User | None:
        """
            **get_by_email**
        :param email:
        :return:
        """
        if not email:
            return None
        for user in self.users.values():
            if user.email.casefold() == email.casefold():
                return user

        with self.get_session() as session:
            user_data: UserORM = session.query(UserORM).filter(UserORM.email == email.casefold()).first()

            return User(**user_data.to_dict()) if user_data else None

    @error_handler
    async def send_password_reset(self, email: str) -> dict[str, str] | None:
        """
        Sends a password reset email to the specified email address.

        :param email: The email address to send the password reset email to.
        :return: A dictionary containing the result of the email sending operation, or None if an error occurred.
        """
        # TODO please complete the method to send the password reset email
        password_reset_subject: str = "Rental-Manager.site Password Reset Request"
        # Assuming you have a function to generate the password reset link
        password_reset_link: str = self.generate_password_reset_link(email)

        html = f"""
        <html>
        <body>
            <h2>Rental-Manager.site Password Reset</h2>
            <p>Hello,</p>
            <p>We received a password reset request for your Rental Manager account. 
            Please click the link below to reset your password:</p>
            <a href="{password_reset_link}">{password_reset_link}</a>
            <p>If you didn't request a password reset, you can ignore this email.</p>
            <p>Thank you,</p>
            <p>The Rental Manager Team</p>
        </body>
        </html>
        """

        email_template = dict(to_=email, subject_=password_reset_subject, html_=html)
        await send_mail.send_mail_resend(email=EmailModel(**email_template))

        return email_template

    def generate_password_reset_link(self, email: str) -> str:
        """
        Generates a password reset link for the specified email.

        :param email: The email address for which to generate the password reset link.
        :return: The password reset link.
        """
        token = str(uuid.uuid4())  # Assuming you have a function to generate a random token
        self._verification_tokens[token] = int(time.time())
        password_reset_link = f"https://rental-manager.site/admin/reset-password?token={token}&email={email}"

        return password_reset_link


    async def post(self, user: CreateUser) -> User | None:
        """

        :param user:
        :return:
        """
        with self.get_session() as session:
            user_data: UserORM = session.query(UserORM).filter(or_(UserORM.game_id == user.game_id,
                                                                   UserORM.email == user.email)).first()
            if user_data:
                return None

            new_user: UserORM = UserORM(**user.to_dict())
            session.add(new_user)
            new_user_dict = new_user.to_dict()
            session.commit()
            _user_data = User(**new_user_dict) if isinstance(new_user, UserORM) else None
            self.users[_user_data.game_id] = _user_data
            return _user_data

    @error_handler
    async def put(self, user: User) -> dict[str, str] | None:
        with self.get_session() as session:
            user_data: UserORM = session.query(UserORM).filter_by(game_id=user.game_id).first()
            if not user_data:
                return None

            # Update user_data with the values from the user Pydantic BaseModel
            for field in user_data.__table__.columns.keys():
                if hasattr(user, field):
                    setattr(user_data, field, getattr(user, field))

            # Save the updated user_data back to the session
            session.add(user_data)
            session.commit()
            self.users[user_data.game_id] = user_data
            return user_data.to_dict()

    @error_handler
    async def login(self, username: str, password: str) -> User | None:
        with self.get_session() as session:
            user_data: UserORM = session.query(UserORM).filter_by(username=username).first()
            try:
                if user_data:
                    user: User = User(**user_data.to_dict())
                else:
                    return None
            except ValidationError as e:
                raise UnauthorizedError(description="Cannot Login User please check your login details")
            return user if user.is_login(password=password) else None

    @error_handler
    async def send_verification_email(self, user: User) -> None:
        """
        Sends a verification email to the specified user.

        :param user: The user to send the verification email to.
        """
        token = str(uuid.uuid4())  # Assuming you have a function to generate a verification token
        verification_link = f"https://rental-manager.site/dashboard/verify-email?token={token}&email={user.email}"
        self._verification_tokens[token] = dict(email=user.email, timestamp=int(time.time()))
        # Render the email template
        email_html = render_template("email_templates/verification_email.html", user=user,
                                     verification_link=verification_link)

        msg = EmailModel(subject_="Rental-Manager.site Email Verification",
                         to_=user.email,
                         html_=email_html)

        await send_mail.send_mail_resend(email=msg)

    @error_handler
    async def verify_email(self, email: str, token: str) -> bool:
        """
            **verify_email**
        :param email:
        :param token:
        :return:
        """
        if email is None:
            return False
        if token is None:
            return False
        if token not in self._verification_tokens:
            return False

        _data: dict[str, str | int] = self._verification_tokens[token]

        current_time: int = int(time.time())
        elapsed_time = current_time - int(_data.get('timestamp', 0))
        return (elapsed_time < self._time_limit) and (email.casefold() == _data.get('email'))
