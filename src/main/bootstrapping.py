def bootstrapper():
    from src.database.sql.user import UserORM, ProfileORM, PayPalORM
    from src.database.sql.notifications import NotificationORM
    from src.database.sql.game import GameIDSORM, GiftCodesORM, RedeemCodesORM

    classes_to_create = [UserORM, PayPalORM, ProfileORM, NotificationORM, GameIDSORM, GiftCodesORM, RedeemCodesORM]

    for cls in classes_to_create:
        cls.create_if_not_table()
