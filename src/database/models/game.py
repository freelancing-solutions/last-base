from pydantic import BaseModel, Field


class GameAuth(BaseModel):
    game_id: str
    game_email: str
    game_password: str
    game_pin: str | None


class GameIDS(BaseModel):
    game_id_list: list[str]
