from pydantic import BaseModel
from typing import List


# Модель базового пользователя
class UserBase(BaseModel):
    username: str


# Модель пользователя для авторизации
class UserAuth(UserBase):
    password: str


# Модель пользователя
class User(UserBase):
    id: int

    model_config = {
        "from_attributes": True
    }


# Модель списка пользователей
class UserList(BaseModel):
    users: List[User]