from datetime import date, datetime


from pydantic import BaseModel, Field, Extra


class GameAuth(BaseModel):
    game_id: str
    game_email: str
    game_password: str
    game_pin: str | None


class GameIDS(BaseModel):
    game_id_list: list[str]


class GameDataInternal(BaseModel):
    owner_game_id: str
    game_id: str
    game_uid: str
    base_level: int
    state: int
    base_name: str
    power: int
    last_login_time: datetime

    @classmethod
    def from_json(cls, data, game_id: str, owner_game_id: str):
        return cls(
            owner_game_id=owner_game_id,
            game_id=game_id,
            game_uid=data.get('gameUid'),
            base_level=int(data.get('level')),
            state=data.get('sid'),  # Assuming 'result' corresponds to 'state' in GameDataInternal
            base_name=data.get('name'),
            power=int(data.get('power')),
            last_login_time=datetime.strptime(data.get('lastTime'), "%Y-%m-%d %H:%M:%S")
        )


class GiftCode(BaseModel):
    code: str
    number_days_valid: int

    class Config:
        extra = Extra.ignore


class GiftCodeOut(BaseModel):
    code: str
    number_days_valid: int
    is_valid: bool
    date_submitted: date


class RedeemCodes(BaseModel):
    id: str
    game_id: str
    code: str
