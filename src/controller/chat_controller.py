import datetime
import random

from src.controller import Controllers, error_handler
from src.database.models.email_service import EmailService, EmailSubscriptions
from src.database.models.support_chat import ChatMessage, ChatUser
from src.database.models.users import User
from src.database.sql.email_service import EmailServiceORM, EmailSubscriptionsORM
from src.database.sql.support_chat import ChatMessageORM, ChatUserORM

def create_colour():
    # Generate a random color code in hexadecimal format
    color_code = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    return color_code


class ChatController(Controllers):
    def __init__(self):
        super().__init__()
        self.user_colour = {}

    def init_app(self, app):
        super().init_app(app=app)


    def add_chat_message(self, message: ChatMessage):
        """
            Add Message to Database
        :param message:
        :return:
        """
        with self.get_session() as session:
            chat_message_orm = session.query(ChatMessageORM).filter(
                ChatMessageORM.message_id == message.message_id).first()
            # TODO please consider saving a list of users in this class

            if isinstance(chat_message_orm, ChatMessageORM):
                return message
            chat_message_orm = ChatMessageORM(uid=message.uid,
                                              message_id=message.message_id,
                                              text=message.text,
                                              timestamp=message.timestamp)
            session.add(chat_message_orm)
            session.commit()

            if message.uid not in self.user_colour.keys():
                self.user_colour[message.uid] = create_colour()

            message.user_colour = self.user_colour[message.uid]

            return message

    async def get_all_messages(self) -> list[ChatMessage]:
        """
            Get All Messages from database
        :return:
        """
        with self.get_session() as session:
            print("Entering Get ALL Messages")
            chat_messages_orm_list = session.query(ChatMessageORM).all()
            chat_users_orm_list = session.query(ChatUserORM).all()

            chat_users = [ChatUser(**user.to_dict()) for user in chat_users_orm_list]
            chat_messages = [ChatMessage(**message.to_dict()) for message in chat_messages_orm_list if
                             isinstance(message, ChatMessageORM)]
            # print(f"Found Original Chat Messages : {len(chat_messages)}")
            proc_messages = []
            for message in chat_messages:
                if message.uid not in self.user_colour.keys():
                    self.user_colour[message.uid] = create_colour()

                message.user_colour = self.user_colour[message.uid]
                proc_messages.append(message)

                # for user in chat_users:
                #     if user.uid == message.uid:
                #         print(user.colour)
                #         message.user_colour = user.colour

            # print(f"Proc Messages : {len(proc_messages)}")

            return proc_messages




