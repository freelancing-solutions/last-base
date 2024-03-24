import requests
from flask import Flask
from src.controller import Controllers, error_handler
from src.database.models.market import SellerAccount, BuyerAccount
from src.database.models.users import User
from src.database.sql.market import SellerAccountORM, BuyerAccountORM


class MarketController(Controllers):

    def __init__(self):
        super().__init__()

    def init_app(self, app: Flask):
        super().init_app(app=app)

    @error_handler
    async def activate_seller_account(self, user: User, activate: bool) -> SellerAccount:
        with self.get_session() as session:
            # Check if seller account exists for the user
            seller_account_orm = session.query(SellerAccountORM).filter(SellerAccountORM.uid == user.uid).first()

            if isinstance(seller_account_orm, SellerAccountORM):
                # If account exists, update activation status
                seller_account_orm.account_activated = activate
                session.merge(seller_account_orm)
            else:
                # If account doesn't exist, create a new one and activate it
                seller_account_orm = SellerAccountORM(uid=user.uid, account_activated=True)
                session.add(seller_account_orm)

            session.commit()  # Commit changes to the database

            # Return the corresponding SellerAccount object
            return SellerAccount(**seller_account_orm.to_dict()) if seller_account_orm else SellerAccount(
                uid=user.uid, account_activated=True)

    @error_handler
    async def activate_buyer_account(self, user: User, activate: bool):
        with self.get_session() as session:
            buyer_account_orm: BuyerAccountORM = session.query(BuyerAccountORM).filter(BuyerAccountORM.uid == user.uid).first()

            if isinstance(buyer_account_orm, BuyerAccountORM):
                buyer_account_orm.account_activated = activate

                session.merge(buyer_account_orm)
            else:
                buyer_account_orm = BuyerAccountORM(uid=user.uid, account_activated=True)
                session.add(buyer_account_orm)

            session.commit()

            return BuyerAccount(**buyer_account_orm.to_dict()) if buyer_account_orm else BuyerAccount(uid=user.uid,
                                                                                                      account_activated=True)

    @error_handler
    async def get_buyer_account(self, uid: str) -> BuyerAccount:
        with self.get_session() as session:
            buyer_account_orm = session.query(BuyerAccountORM).filter(BuyerAccountORM.uid == uid).first()
            if isinstance(buyer_account_orm, BuyerAccountORM):
                return BuyerAccount(**buyer_account_orm.to_dict())

            buyer_account = BuyerAccount(uid=uid)
            session.add(BuyerAccountORM(**buyer_account.dict()))
            session.commit()
            return buyer_account

    @error_handler
    async def get_seller_account(self, uid: str) -> SellerAccount:
        with self.get_session() as session:
            seller_account_orm = session.query(SellerAccountORM).filter(SellerAccountORM.uid == uid).first()
            if isinstance(seller_account_orm, SellerAccountORM):
                return SellerAccount(**seller_account_orm.to_dict())
            seller_account = SellerAccount(uid=uid)
            session.add(SellerAccountORM(**seller_account.dict()))
            session.commit()
            return seller_account

    @error_handler
    async def approved_for_market(self, uid: str, is_approved: bool = False):
        with self.get_session() as session:
            seller_account_orm = session.query(SellerAccountORM).filter(SellerAccountORM.uid == uid).first()
            if isinstance(seller_account_orm, SellerAccountORM):
                seller_account_orm.account_verified = is_approved

                session.merge(seller_account_orm)

                session.commit()
                return True
            return False
