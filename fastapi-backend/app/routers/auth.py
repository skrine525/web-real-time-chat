import datetime
from jose import jwt
from sqlalchemy import orm
from fastapi import  Depends, HTTPException, status
from fastapi.routing import APIRouter
from app.utils import auth
from app.database import operations, get_db
from app.schemas import token as token_schema
from app.schemas import user as user_schema


router = APIRouter(prefix="/auth") 


# Эндпоинт для регистрации пользователя
@router.post("/register", response_model=token_schema.Token, tags=["auth"], summary="Регистрации пользователя")
def register_user(user: user_schema.UserAuth, db: orm.Session = Depends(get_db)):
    """
    ## Регистрация пользователя
    
    Регистрирует нового пользователя в системе. Если имя пользователя уже существует, возвращается ошибка 400.

    ### Пример тела запроса:
    ```json
    {
        "username": "user",
        "password": "password"
    }
    ```

    ### Возможные ответы:
    - **200 OK**: Возвращает JSON с токеном доступа, если регистрация прошла успешно.
    - **400 BAD REQUEST**: Возвращается, если имя пользователя уже зарегистрировано.

    ### Пример успешного ответа:
    ```json
    {
        "access_token": "token"
    }
    ```

    ### Ошибки:
    - **400**: "Username already registered" — если пользователь с таким именем уже существует.

    ### Заметки:
    - Токен доступа действителен в течение определенного времени, указанного в конфигурации.
    """
    
    db_user = operations.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    db_user = operations.create_user(db=db, user=user)

    access_token_expires = datetime.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = jwt.encode(
        {"sub": db_user.username, "exp": datetime.datetime.now(datetime.timezone.utc) + access_token_expires},
        auth.SECRET_KEY,
        algorithm=auth.ALGORITHM,
    )
    
    return {"access_token": access_token}

# Эндпоинт для аутентификации пользователя
@router.post("/login", response_model=token_schema.Token, tags=["auth"], summary="Аутентификация пользователя")
async def login_endpoint(credentials: user_schema.UserAuth, db: orm.Session = Depends(get_db)):
    """
    ## Аутентификация пользователя
    
    Позволяет получить токен авторизации пользователя по логину и паролю. Если имя пользователя или пароль неверные, возвращается ошибка 401.

    ### Пример тела запроса:
    ```json
    {
        "username": "user",
        "password": "password"
    }
    ```

    ### Возможные ответы:
    - **200 OK**: Возвращает JSON с токеном доступа, если регистрация прошла успешно.
    - **401 UNAUTHORIZED**: Возвращается, если имя пользователя или пароль неверные.

    ### Пример успешного ответа:
    ```json
    {
        "access_token": "token"
    }
    ```

    ### Ошибки:
    - **401**: "Incorrect username or password" — если неверный логин или пароль.

    ### Заметки:
    - Токен доступа действителен в течение определенного времени, указанного в конфигурации.
    """
    
    user = operations.get_user_by_username(db, username=credentials.username)
    if not user or not auth.pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    access_token_expires = datetime.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = jwt.encode(
        {"sub": user.username, "exp": datetime.datetime.now(datetime.timezone.utc) + access_token_expires},
        auth.SECRET_KEY,
        algorithm=auth.ALGORITHM,
    )
    
    return {"access_token": access_token}
