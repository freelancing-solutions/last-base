from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field, Extra


class SellerAccount(BaseModel):
    uid: str
    seller_rating: int
    seller_name: str
    promotional_content: str
    account_verified: bool
    total_accounts_sold: int
    total_amount_sold: int


class BuyerAccount(BaseModel):
    uid: str
    buyer_rating: int
    buyer_name: int
    account_verified: bool

    total_accounts_bought: int
    total_skins_bought: int

    total_amount_spent: int
    amount_in_escrow: int


class Farms(BaseModel):
    uid: str
    package_id: str

    state: int
    average_base_level: int
    total_farms: int
    total_bought: int = Field(default=0)
    item_price: int
    package_price: int
    farm_manager_available: bool
    image_url: str
    accounts_verified: bool
    notes: str

    def farms_remaining(self):
        return self.total_farms - self.total_bought


class FarmResources(BaseModel):
    """
        Average Resources Per Farm
    """
    package_id: str
    total_iron: int
    total_wood: int
    total_oil: int
    total_food: int
    total_money: int


class FarmIDS(BaseModel):
    """
        List of Farms Being Sold
    """
    package_id: str
    uid: str
    game_id: str
    game_uid: str
    base_level: int
    state: int
    base_name: str
    base_level: int
    power: int


class FarmCredentials(BaseModel):
    game_id: str
    account_email: str
    password: str
    pin: str | None
