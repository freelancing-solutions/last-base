import uuid

from pydantic import BaseModel, Field


class Auth(BaseModel):
    username: str
    password: str
    remember: str | None


def generate_uuid_str():
    return str(uuid.uuid4())[:32]


class RegisterUser(BaseModel):
    uid: str = Field(default_factory=generate_uuid_str)
    username: str
    email: str
    password: str
    terms: str
