from fastapi import  Depends
from fastapi.routing import APIRouter
from app.schemas import user as user_schema
from app.utils.auth import get_current_user


router = APIRouter(prefix="/users") 


# Эндпоинт для получения информации о текущем пользователе
@router.get("/me", response_model=user_schema.User, tags=["users"], summary="Информация о текущем пользователе")
async def get_current_user(current_user: user_schema.User = Depends(get_current_user)):
    """
    ## Информация о текущем пользователе
    
    Позволяет получить информацию о текущем авторизованном пользователе, используя его токен доступа.

    ### Пример запроса:
    Запрос делается с использованием токена в заголовке:

    ```http
    GET /me
    Authorization: Bearer <токен>
    ```

    ### Возможные ответы:
    - **200 OK**: Возвращает информацию о текущем пользователе.
    - **401 UNAUTHORIZED**: Возвращается, если токен авторизации недействителен или отсутствует.
    
    ### Пример успешного ответа:
    ```json
    {
        "id": 1,
        "username": "user"
    }
    ```

    ### Ошибки:
    - **401**: "Unauthorized" — если токен авторизации отсутствует или недействителен.
    
    ### Заметки:
    - Пользователь должен быть авторизован, чтобы получить доступ к этому эндпоинту.
    - Токен должен быть передан в заголовке Authorization как `Bearer token`.
    """
    
    return current_user