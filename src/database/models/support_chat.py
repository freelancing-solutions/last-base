import uuid
from datetime import datetime
from pydantic import BaseModel, Field, Extra


def timestamp() -> str:
    return str(datetime.utcnow())


def create_id() -> str:
    return str(uuid.uuid4())


class ChatUser(BaseModel):
    uid: str
    display_name: str
    user_banned: bool = Field(default=False)


class ChatMessage(BaseModel):
    uid: str
    message_id: str = Field(default_factory=create_id)
    text: str
    timestamp: str = Field(default_factory=timestamp)
