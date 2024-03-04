from sqlalchemy import Column, Integer, String, Text, Boolean, Date, ForeignKey, inspect
from datetime import date
from src.database.constants import ID_LEN, NAME_LEN
from src.database.sql import Base, engine


class CompanyORM(Base):
    __tablename__ = 'companies'

    company_id: str = Column(String(ID_LEN), primary_key=True)
    company_name: str = Column(String(NAME_LEN))
    description: str = Column(Text)
    address_line_1: str = Column(String(255))
    address_line_2: str = Column(String(255))
    city: str = Column(String(NAME_LEN))
    postal_code: str = Column(String(8))
    province: str = Column(String(NAME_LEN))
    country: str = Column(String(NAME_LEN))
    contact_number: str = Column(String(13))
    website: str = Column(String(255))

    def to_dict(self):
        """
        Convert the CompanyORM instance to a dictionary.
        :return: Dictionary representation of the instance.
        """
        return {
            "company_id": self.company_id,
            "company_name": self.company_name,
            "description": self.description,
            "address_line_1": self.address_line_1,
            "address_line_2": self.address_line_2,
            "city": self.city,
            "postal_code": self.postal_code,
            "province": self.province,
            "country": self.country,
            "contact_number": self.contact_number,
            "website": self.website
        }

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)


class UserCompanyORM(Base):
    __tablename__ = 'user_company'
    id: str = Column(String(ID_LEN), primary_key=True)
    company_id: str = Column(String(ID_LEN), index=True)
    user_id: str = Column(String(ID_LEN), index=True)
    user_level: str = Column(String(NAME_LEN), default="admin")

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)


class TenantCompanyORM(Base):
    __tablename__ = 'tenant_company'
    id: str = Column(String(ID_LEN), primary_key=True)
    company_id: str = Column(String(ID_LEN), index=True)
    tenant_id: str = Column(String(ID_LEN), index=True)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)
