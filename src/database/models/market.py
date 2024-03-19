from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field, Extra


class SellerAccount(BaseModel):
    """
        A Strcuture needed for Sellers to sell their Farms
    """
    uid: str
    seller_rating: int  # A Rating of 1 to 10 Based on Feedback
    seller_name: str
    promotional_content: str
    account_verified: bool
    total_items_sold: int  # Farms, Accounts and Skins

    total_amount_sold: int  # Amount Sold in Dollars


class BuyerAccount(BaseModel):
    uid: str
    buyer_rating: int  # A Rating of 1 to 10 Based on Feedback
    buyer_name: int  # Name of the Buyer , Could Also be a nickname
    account_verified: bool

    total_accounts_bought: int
    total_skins_bought: int

    total_amount_spent: int  # Amount Spent in Dollars
    amount_in_escrow: int  # Amount the buyer puts in Escrow to secure a sale


#################################################################################################

class FarmSale(BaseModel):
    uid: str  # ID of the user selling the Farm
    package_id: str # ID of the Packaged Deal

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


#################################################################################################


class MainAccounts(BaseModel):
    """
        A Structure that allows users to sell Main Accounts
    """
    uid: str  # ID of the user making the Account Sale
    state: int  # The State number the Account is in
    base_level: int  # Base Level of the Account
    item_price: int  # Price for the Account

    image_url: str

    total_gold_cards: int
    universal_sp_medals: int
    total_skins: int

    season_heroes: int
    sp_heroes: int
    amount_spent_packages: int  # Amount Spent on Packages
    vip_shop: bool
    energy_lab_level: int
    energy_lab_password: str


class MainAccountsCredentials(BaseModel):
    game_id: str
    account_email: str
    account_password: str
    account_pin: str
