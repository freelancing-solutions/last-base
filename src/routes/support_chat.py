from flask import Blueprint, render_template
from flask_socketio import emit

from src.main import chat_io

chat_route = Blueprint('chat', __name__)


@chat_route.get('/chat/support')
async def get_chat():
    return render_template('support_chat/chat.html')


@chat_io.on('message')
def handle_message(message):
    emit('message', message, broadcast=True)
