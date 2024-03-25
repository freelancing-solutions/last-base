import datetime

from src.controller import Controllers, error_handler
from src.database.models.email_service import EmailService, EmailSubscriptions
from src.database.models.support_chat import ChatMessage
from src.database.models.users import User
from src.database.sql.email_service import EmailServiceORM, EmailSubscriptionsORM
from src.database.sql.support_chat import ChatMessageORM


class ChatController(Controllers):
    def __init__(self):
        super().__init__()

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
            if isinstance(chat_message_orm, ChatMessageORM):
                return message
            chat_message_orm = ChatMessageORM(**message.dict())
            session.add(chat_message_orm)
            session.commit()
            return message

    async def get_all_messages(self) -> list[ChatMessage]:
        """
            Get All Messages from database
        :return:
        """
        with self.get_session() as session:
            chat_messages_orm_list = session.query(ChatMessageORM).all()
            return [ChatMessage(**message.to_dict()) for message in chat_messages_orm_list if
                    isinstance(message, ChatMessageORM)]
