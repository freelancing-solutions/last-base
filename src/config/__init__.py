from pydantic import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    SECRET_KEY: str = '123'


@lru_cache(maxsize=1)
def create_config() -> Settings:
    """
        **will initialize and return settings file**
    :return:
    """
    return Settings()
