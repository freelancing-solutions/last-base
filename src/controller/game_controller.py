import time
import uuid

from flask import Flask, render_template
from pydantic import ValidationError
from sqlalchemy import or_

from src.controller import error_handler, UnauthorizedError, Controllers
from src.database.models.game import GameAuth
from src.database.models.profile import Profile, ProfileUpdate
from src.database.models.users import User, CreateUser, UserUpdate
from src.database.sql.game import GameAuthORM
from src.database.sql.user import UserORM, ProfileORM
from src.emailer import EmailModel
from src.main import send_mail
import requests


class GameController(Controllers):

    def __init__(self):
        super().__init__()

    def init_app(self, app: Flask):
        super().init_app(app=app)

    async def create_account_verification_request(self, game_data: GameAuth) -> GameAuth:
        """

        :param game_data:
        :return:
        """
        with self.get_session() as session:
            account_verification: GameAuthORM = session.Query(GameAuthORM.game_id == game_data.game_id).first()
            if account_verification and account_verification.game_id == game_data.game_id:
                return GameAuth(**GameAuthORM.to_dict())

            game_orm = GameAuthORM(**game_data.dict())
            session.add(game_orm)
            session.commit()
            return game_data
