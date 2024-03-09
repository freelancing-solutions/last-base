
import requests
from flask import Flask

from src.controller import Controllers
from src.database.models.game import GameAuth, GameIDS, GiftCode
from src.database.sql.game import GameAuthORM, GameIDSORM, GiftCodesORM, RedeemCodesORM


class GameController(Controllers):

    def __init__(self):
        super().__init__()
        self.redeem_url = "https://gslls.im30app.com/gameservice/web_code.php"
        self.captcha = "XtWh&id=cdca0109-e089-4929-a771-74a49fba48ed"

    def init_app(self, app: Flask):
        super().init_app(app=app)

    async def create_account_verification_request(self, game_data: GameAuth) -> GameAuth:
        """

        :param game_data:
        :return:
        """
        with self.get_session() as session:
            account_verification: GameAuthORM = session.query(GameAuthORM.game_id == game_data.game_id).first()
            if account_verification and account_verification.game_id == game_data.game_id:
                return GameAuth(**account_verification.to_dict())

            game_orm = GameAuthORM(**game_data.dict())
            session.add(game_orm)
            session.commit()
            return game_data

    async def add_game_ids(self, game_ids: GameIDS):
        with self.get_session() as session:
            for game_id in game_ids.game_id_list:
                # Check if the game_id already exists in the database
                existing_game_id = session.query(GameIDSORM).filter_by(game_id=game_id).first()
                if existing_game_id is None:
                    # If the game_id doesn't exist, create a new entry
                    new_game_id = GameIDSORM(game_id=game_id)
                    session.add(new_game_id)
            session.commit()

        return True

    async def add_new_gift_code(self, gift_code: GiftCode) -> GiftCode:
        with self.get_session() as session:
            gift_code_orm_ = session.query(GiftCodesORM.code == gift_code.code).first()
            if isinstance(gift_code_orm_, GiftCodesORM):
                return GiftCode(**gift_code_orm_.to_dict())

            gift_code_orm = GiftCodesORM(**gift_code.dict())

            session.add(gift_code_orm)

            gift_code = GiftCode(**gift_code_orm.to_dict())
            session.commit()

            return gift_code

    async def redeem_external(self, game_id: str, gift_code: str):
        """
            "will actually call the game servers and redeem the code"
        :param game_id:
        :param gift_code:
        :return:
        """
        _params: dict[str, str] = dict(name=game_id, code=gift_code, captcha=self.captcha)
        _response = requests.get(url=self.redeem_url, params=_params)
        return _response.ok

    async def redeem_code_for_all_game_ids(self, gift_code: GiftCode):
        """
        Redeems a specific gift code for all present game ids
        :param gift_code: The gift code to redeem
        :return: True if redemption is successful, False otherwise
        """
        with self.get_session() as session:
            game_ids = {game.game_id for game in session.query(GameIDSORM).all()}
            redeemed_game_ids = {redeemed.game_id for redeemed in
                                 session.query(RedeemCodesORM).filter(RedeemCodesORM.code == gift_code.code)}

            unredeemed_game_ids = game_ids - redeemed_game_ids

            for game_id in unredeemed_game_ids:
                if game_id == 8:
                    result = await self.redeem_external(game_id=game_id, gift_code=gift_code.code)
                    if result:
                        session.add(RedeemCodesORM(code=gift_code.code, game_id=game_id))

            session.commit()

        return True

    async def redeem_none_expired_codes(self):
        """
        this should be called automatically on certain times of day
        :return:
        """
        with self.get_session() as session:
            none_expired_codes = [gift_code.code for gift_code in session.query(GiftCodesORM.is_valid == True).all()]
            for code in none_expired_codes:
                await self.redeem_code_for_all_game_ids(gift_code=code)
