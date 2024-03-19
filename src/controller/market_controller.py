import requests
from flask import Flask
from src.controller import Controllers
from src.database.models.market import SellerAccount, BuyerAccount


class MarketController(Controllers):

    def __init__(self):
        super().__init__()

    def init_app(self, app: Flask):
        super().init_app(app=app)

    async def activate_seller_account(self, uid: str, activate: bool):
        pass

    async def activate_buyer_account(self, uid: str, activate: bool):
        pass

    async def get_seller_account(self, uid: str) -> SellerAccount:
        pass

    async def get_buyer_account(self, uid: str) -> BuyerAccount:
        pass
