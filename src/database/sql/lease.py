from datetime import date

from sqlalchemy import Column, Date, Boolean, String, Integer, Text, inspect

from src.database.constants import ID_LEN, NAME_LEN
from src.database.sql import Base, engine


class LeaseAgreementORM(Base):
    __tablename__ = 'lease_agreement'
    agreement_id: str = Column(String(ID_LEN), primary_key=True, unique=True)
    property_id: str = Column(String(ID_LEN))
    unit_id: str = Column(String(ID_LEN))
    tenant_id: str = Column(String(ID_LEN))
    start_date: date = Column(Date)
    end_date: date = Column(Date)
    rent_amount: int = Column(Integer)
    deposit_amount: int = Column(Integer)
    is_active: bool = Column(Boolean)
    payment_period: str = Column(String(NAME_LEN))

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    def to_dict(self) -> dict[str, str | date | bool | int]:
        return {
            'agreement_id': self.agreement_id,
            'property_id': self.property_id,
            'unit_id': self.unit_id,
            'tenant_id': self.tenant_id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'rent_amount': self.rent_amount,
            'deposit_amount': self.deposit_amount,
            'is_active': self.is_active
        }


class LeaseAgreementTemplate(Base):
    __tablename__ = 'lease_agreement_template'

    template_id: str = Column(String(ID_LEN), primary_key=True, unique=True)
    property_id: str = Column(String(ID_LEN))
    template_name: str = Column(String(NAME_LEN))
    template_text: str = Column(Text)
    is_default: bool = Column(Boolean)

    @classmethod
    def create_if_not_table(cls):
        if not inspect(engine).has_table(cls.__tablename__):
            Base.metadata.create_all(bind=engine)

    def to_dict(self) -> dict[str, str | bool]:
        return {
            'template_id': self.template_id,
            'property_id': self.property_id,
            'template_name': self.template_name,
            'template_text': self.template_text,
            'is_default': self.is_default
        }