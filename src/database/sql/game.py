import uuid

from sqlalchemy import Column, String, inspect, ForeignKey, Boolean

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


class GameIDSORM(Base):
    __tablename__ = "gameids"
    game_id: str = Column(String(ID_LEN), primary_key=True)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    def to_dict(self):
        return {
            'game_id': self.game_id
        }


class GiftCodesORM(Base):
    __tablename__ = "gift_codes"
    code = Column(String(NAME_LEN), primary_key=True)
    is_valid = Column(Boolean, default=True)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    def to_dict(self):
        return {
            'code': self.code,
            'is_valid': self.is_valid
        }


# noinspection PyRedeclaration
class RedeemCodesORM(Base):
    __tablename__ = "redeem_codes"

    id = Column(String(ID_LEN), primary_key=True, default=str(uuid.uuid4()))
    game_id = Column(String(ID_LEN), ForeignKey('gameids.game_id'))
    code = Column(String(NAME_LEN), ForeignKey('gift_codes.code'))

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    def to_dict(self):
        return {
            'id': self.id,
            'game_id': self.game_id,
            'code': self.code
        }
