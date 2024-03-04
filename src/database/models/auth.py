

from pydantic import BaseModel, Field


class Auth(BaseModel):
    username: str
    password: str
    remember: str | None


class RegisterUser(BaseModel):
    username: str
    game_id: str
    email: str
    password: str
    terms: str
