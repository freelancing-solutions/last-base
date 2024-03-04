
def bootstrapper():
    from src.database.sql.user import UserORM
    from src.database.sql.user import ProfileORM
    from src.database.sql.notifications import NotificationORM


    classes_to_create = [UserORM, ProfileORM, NotificationORM]

    for cls in classes_to_create:
        cls.create_if_not_table()
