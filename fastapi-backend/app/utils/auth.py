from fastapi import  Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import orm
from jose import JWTError, jwt
from passlib.context import CryptContext
from app import config
from app.database import operations, get_db


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


SECRET_KEY = config.SECRET_KEY                                      # Секретный ключ
ALGORITHM = "HS256"                                                 # Алгоритм шифрования
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES    # Время жизни токена


# Позволяет получить объект пользователя по токену
async def get_user_by_token(db: orm.Session, token: str):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = operations.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    
    return user

# Позволяет получить объект пользователя по Bearer авторизации
async def get_current_user(token: str = Depends(oauth2_scheme), db: orm.Session = Depends(get_db)):
    return await get_user_by_token(db, token)