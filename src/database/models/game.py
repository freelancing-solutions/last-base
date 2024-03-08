from pydantic import BaseModel, Field


class GameAuth(BaseModel):
    game_id: str
    game_email: str
    game_password: str
    game_pin: str | None


class GameIDS(BaseModel):
    game_id_list: list[str]


class GiftCode(BaseModel):
    code: str
    is_valid: bool


class RedeemCodes(BaseModel):
    id: str
    game_id: str
    code: str
