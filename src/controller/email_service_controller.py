from flask import Flask
from pydantic import PositiveInt

from src.controller import Controllers
from src.database.models.email_service import EmailService
from src.database.models.users import User
from src.database.models.wallet import Wallet, WalletTransaction, TransactionType
from src.database.sql.email_service import EmailServiceORM
from src.database.sql.wallet import WalletTransactionORM


class EmailController(Controllers):
    def __init__(self):
        super().__init__()

    def init_app(self, app):
        super().init_app(app=app)

    async def create_email_subscription(self, email_service: EmailService) -> EmailService:
        with self.get_session() as session:
            email_services = session.query(EmailServiceORM).filter(EmailServiceORM.uid == email_service.uid,
                                                                   EmailServiceORM.subscription_active == False).all()
            for email_service in email_services:
                session.delete(email_service)

            email_service_orm = EmailServiceORM(**email_service.dict())
            session.add(email_service_orm)

            session.commit()
            return email_service

    async def activation_email_service(self, user: User, activate: bool) -> bool:
        with self.get_session() as session:
            email_service_orm = session.query(EmailServiceORM).filter(EmailService.uid == user.uid).first()
            if isinstance(email_service_orm, EmailServiceORM):
                email_service_orm.subscription_active = activate
                session.merge(email_service_orm)
                session.commit()

                return  True
            return False

    async def get_email_subscription(self, user: User) -> EmailService | None:
        with self.get_session() as session:
            email_service_orm = session.query(EmailServiceORM).filter(EmailService.uid == user.uid).first()
            if isinstance(email_service_orm, EmailServiceORM):
                return EmailService(**email_service_orm.to_dict())
            else:
                return None
