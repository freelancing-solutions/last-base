from sqlalchemy import Column, String, inspect

from src.database.constants import ID_LEN, NAME_LEN
from src.database.sql import Base, engine


class GameAuthORM(Base):
    __tablename__ = 'game_auth'
    game_id: str = Column(String(ID_LEN), primary_key=True)
    game_email: str = Column(String(ID_LEN))
    game_password: str = Column(String(NAME_LEN))
    game_pin: str | None = Column(String(ID_LEN))

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    def to_dict(self):
        return {
            'game_id': self.game_id,
            'game_email': self.game_email,
            'game_password': self.game_password,
            'game_pin': self.game_pin
        }
