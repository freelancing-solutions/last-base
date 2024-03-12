from sqlalchemy import Column, String, Boolean, ForeignKey, inspect, Integer

from src.database.constants import ID_LEN, NAME_LEN
from src.database.sql import Base, engine


class UserORM(Base):
    """
    User Model
        User ORM
    """
    __tablename__ = 'users'

    game_id: str = Column(String(ID_LEN), primary_key=True, unique=True)
    username: str = Column(String(NAME_LEN))
    password_hash: str = Column(String(255))
    email: str = Column(String(256))
    account_verified: bool = Column(Boolean, default=False)
    is_system_admin: bool = Column(Boolean, default=False)


    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    def __init__(self,
                 game_id: str,
                 username: str,
                 password_hash: str,
                 email: str,
                 account_verified: bool = False,
                 is_system_admin: bool = False
                 ):
        self.game_id = game_id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.account_verified = account_verified
        self.is_system_admin = is_system_admin

    def __bool__(self) -> bool:
        return bool(self.game_id) and bool(self.username) and bool(self.email)

    def to_dict(self) -> dict[str, str | bool]:
        return {
            'game_id': self.game_id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'account_verified': self.account_verified,
            'is_system_admin': self.is_system_admin
        }


class ProfileORM(Base):
    """
        Profile ORM
    """
    __tablename__ = "profile"
    game_id: str = Column(String(ID_LEN), primary_key=True)
    gameUid: str = Column(String(ID_LEN))
    alliancename: str = Column(String(NAME_LEN))
    allianceabr: str = Column(String(3))
    level: int = Column(Integer)
    sid: int = Column(Integer)
    name: str = Column(String(12))
    power: int = Column(Integer)
    lastTime: str = Column(String(24))
    currency: str = Column(String(6))

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    def to_dict(self) -> dict[str, str | int]:
        """
        Convert the ProfileORM instance to a dictionary.
        :return: Dictionary representing the ProfileORM instance.
        """
        return {
            'game_id': self.game_id,
            'gameUid': self.gameUid,
            'alliancename': self.alliancename,
            'allianceabr': self.allianceabr,
            'level': self.level,
            'sid': self.sid,
            'name': self.name,
            'power': self.power,
            'lastTime': self.lastTime,
            'currency': self.currency
        }

    def __eq__(self, other):
        if not isinstance(other, ProfileORM):
            return False
        return self.game_id == other.game_id


class PayPalORM(Base):
    __tablename__ = 'paypal_account'
    game_id = Column(String(NAME_LEN), primary_key=True)
    paypal_email: str = Column(String(NAME_LEN))

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    def to_dict(self) -> dict[str, str]:
        return {
            'game_id': self.game_id,
            'paypal_email': self.paypal_email
        }

