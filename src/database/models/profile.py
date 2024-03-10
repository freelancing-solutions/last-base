from pydantic import BaseModel, Field, Extra


class Profile(BaseModel):
    """
        **Profile**
            allows users to create personalized settings
            such us - deposit multiplier

    """
    game_id: str
    gameUid: str
    alliancename: str | None
    allianceabr: str | None
    level: int = Field(default=3)
    sid: int = Field(default=1)
    name: str
    power: int = Field(default=1024)
    lastTime: str
    currency: str = Field(default="$")

    def __eq__(self, other):
        if not isinstance(other, Profile):
            return False
        return self.game_id == other.game_id


class ProfileUpdate(BaseModel):
    game_id: str
    alliancename: str | None
    allianceabr: str | None

    class Config:
        extra = Extra.ignore
