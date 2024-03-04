from pydantic import BaseModel, Field, Extra


class Profile(BaseModel):
    """
        **Profile**
            allows users to create personalized settings
            such us - deposit multiplier

    """
    game_id: str
    currency: str = Field(default="R")

    def __eq__(self, other):
        if not isinstance(other, Profile):
            return False
        return self.game_id == other.game_id


class ProfileUpdate(BaseModel):
    game_id: str
    currency: str = Field(default="R")

    class Config:
        extra = Extra.ignore
