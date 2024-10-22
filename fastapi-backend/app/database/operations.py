from sqlalchemy import or_
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.schemas import user as user_schema
from app.database import models
from typing import List


# Создания контекста хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Создает пользователя
def create_user(db: Session, user: user_schema.UserAuth) -> models.User:
    hashed_password = pwd_context.hash(user.password)       # Хэшируем пароль
    
    # Создаем пользователя
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password
    )
    
    db.add(db_user)             # Добавляем пользователя в сессию
    db.commit()                 # Коммитим изменения в сессии
    db.refresh(db_user)         # Обновляем поля пользователя
    
    return db_user              # Возвращаем пользователя

# Возвращает пользователя по имени пользователя
def get_user_by_username(db: Session, username: str) -> models.User:
    return db.query(models.User).filter(models.User.username == username).first()

# Возвращает пользователя по идентификатору
def get_user_by_id(db: Session, user_id: int) -> models.User:
    return db.query(models.User).filter(models.User.id == user_id).first()

# Создает сообщение
def create_message(db: Session, sender_id: int, receiver_id: int, text: str) -> models.Message:
    # Создаем сообщение
    message = models.Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        text=text
    )
    
    db.add(message)             # Добавляем сообщение в сессию
    db.commit()                 # Коммитим изменения в сессии
    db.refresh(message)         # Обновляем поля сообщения
    
    return message              # Возвращаем сообщение

# Возвращает все сообщения двух пользователей
def get_messages_by_user_ids(db: Session, user1_id: int, user2_id: int) -> List[models.Message]:
    messages = db.query(models.Message).filter(
        or_(
            models.Message.sender_id.in_([user1_id, user2_id]),
            models.Message.receiver_id.in_([user1_id, user2_id])
        )
    ).all()
    
    return messages
