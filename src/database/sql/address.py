from sqlalchemy import Column, String, inspect

from src.database.constants import ID_LEN, NAME_LEN
from src.database.sql import Base, engine


class AddressORM(Base):
    __tablename__ = 'addresses'

    address_id = Column(String(ID_LEN), primary_key=True)
    street = Column(String(NAME_LEN), index=True)
    city = Column(String(NAME_LEN), index=True)
    state = Column(String(NAME_LEN), index=True)
    postal_code = Column(String(8))
    country = Column(String(NAME_LEN))

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)
