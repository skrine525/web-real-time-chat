from pydantic import BaseModel
from typing import List
from enum import Enum
from . import user


# Типы сообщений
class MessageType(Enum):
    SENT = "sent"
    RECEIVED = "received"


# Модель сообщения
class Message(BaseModel):
    type: str
    text: str


# Модель чата
class Chat(BaseModel):
    user: user.User
    messages: List[Message]