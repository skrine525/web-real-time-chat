from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


# Базовая модель
Base = declarative_base()


# Модель для пользователей
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)                  # ID пользователя
    username = Column(String, unique=True, index=True)                  # Юзернейм пользователя
    hashed_password = Column(String)                                    # Хэш пароля
    telegram_id = Column(Integer, unique=True, default=None)            # Телеграм ID
    
    # Связь с отправленными сообщениями
    sent_messages = relationship("Message", foreign_keys='[Message.sender_id]', back_populates="sender")
    
    # Связь с полученными сообщениями
    received_messages = relationship("Message", foreign_keys='[Message.receiver_id]', back_populates="receiver")


# Модель для сообщений
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)                  # ID сообщения
    sender_id = Column(Integer, ForeignKey("users.id"))                 # Внешний ключ на отправителя
    receiver_id = Column(Integer, ForeignKey("users.id"))               # Внешний ключ на получателя
    text = Column(String, nullable=False)                               # Текст сообщения 
    
    # Связь с отправителем
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    
    # Связь с получателем
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")