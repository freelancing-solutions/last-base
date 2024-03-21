def bootstrapper():
    from src.database.sql.user import UserORM, ProfileORM, PayPalORM
    from src.database.sql.notifications import NotificationORM
    from src.database.sql.game import GameIDSORM, GiftCodesORM, RedeemCodesORM
    from src.database.sql.wallet import WalletTransactionORM, WalletORM
    from src.database.sql.market import BuyerAccountORM, SellerAccountORM
    from src.database.sql.email_service import EmailServiceORM

    classes_to_create = [UserORM, PayPalORM, ProfileORM, NotificationORM, GameIDSORM, GiftCodesORM, RedeemCodesORM,
                         WalletTransactionORM, WalletORM, BuyerAccountORM, SellerAccountORM, EmailServiceORM]

    for cls in classes_to_create:
        cls.create_if_not_table()
