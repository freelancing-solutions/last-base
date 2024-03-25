from flask import Blueprint, render_template, request
from flask_socketio import emit

from src.authentication import login_required
from src.database.models.support_chat import ChatMessage
from src.database.models.users import User
from src.main import chat_io, chat_controller

chat_route = Blueprint('chat', __name__)


@chat_route.get('/chat/support')
@login_required
async def get_chat(user: User):
    context = dict(user=user)
    message_list: list[ChatMessage] = await chat_controller.get_all_messages()
    context.update(message_list=message_list)

    return render_template('support_chat/chat.html', **context)


@chat_io.on('message')
def handle_message(message):
    uid = request.cookies.get('auth')
    print(message)
    _text = message.get('text', "")
    new_message: ChatMessage = ChatMessage(uid=uid, text=_text)
    print(f"New Message: {new_message}")
    _message = chat_controller.add_chat_message(message=new_message)
    emit('message', _message.dict(), broadcast=True)
