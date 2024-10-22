from pydantic import BaseModel


# Модель токена
class Token(BaseModel):
    access_token: str