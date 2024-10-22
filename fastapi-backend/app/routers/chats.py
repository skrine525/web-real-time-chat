import asyncio, json
from fastapi import  Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy import orm
from redis.asyncio import Redis
from app.utils.auth import get_current_user, get_user_by_token
from app.schemas import chat as chat_schema
from app.schemas import user as user_schema
from app.database import models, get_db
from app.database.operations import get_user_by_id, create_message, get_messages_by_user_ids
from app.utils.connection_manager import ConnectionManager


router = APIRouter(prefix="/chats")
redis = Redis(host="chat_redis", db=1, decode_responses=True)
manager = ConnectionManager()


@router.get("", response_model=user_schema.UserList, tags=["chats"], summary="Список чатов")
async def get_all_chats(current_user: user_schema.User = Depends(get_current_user), db: orm.Session = Depends(get_db)):
    """
    ## Получение списка пользователей для чатов

    Позволяет получить список всех пользователей, кроме текущего авторизованного пользователя.
    Это может быть использовано для отображения доступных контактов для начала чата.

    ### Пример запроса:
    Запрос делается с использованием токена в заголовке:

    ```http
    GET /chats
    Authorization: Bearer <токен>
    ```

    ### Пример успешного ответа:
    ```json
    {
        "users": [
            {
                "id": 1,
                "username": "user2"
            },
            {
                "id": 2,
                "username": "user2"
            }
        ]
    }
    ```

    ### Возможные ответы:
    - **200 OK**: Возвращает список всех пользователей, кроме текущего.
    - **401 UNAUTHORIZED**: Возвращается, если токен авторизации недействителен или отсутствует.

    ### Ошибки:
    - **401**: "Unauthorized" — если токен авторизации отсутствует или недействителен.

    ### Заметки:
    - Текущий авторизованный пользователь исключается из списка пользователей.
    - Пользователь должен быть авторизован для доступа к этому эндпоинту.

    """
    
    users =  db.query(models.User).filter(models.User.username != current_user.username).all()
    return user_schema.UserList(users=users)

@router.get("/{user_id}", response_model=chat_schema.Chat, tags=["chats"], summary="Информация о чате")
async def get_chat(user_id, current_user: user_schema.User = Depends(get_current_user), db: orm.Session = Depends(get_db)):
    """
    ## Получение информации о чате

    Позволяет получить чат между текущим авторизованным пользователем и другим пользователем по его ID.
    Возвращает список сообщений, которые были отправлены или получены текущим пользователем.

    ### Параметры:
    - **user_id**: ID пользователя, с которым ведется чат.

    ### Пример запроса:
    Запрос делается с использованием токена в заголовке и включает ID пользователя, с которым необходимо получить чат:

    ```http
    GET /chats/2
    Authorization: Bearer <токен>
    ```

    ### Пример успешного ответа:
    ```json
    {
        "user": {
            "id": 2,
            "username": "user2"
        },
        "messages": [
            {
                "type": "sent",
                "text": "Hello!"
            },
            {
                "type": "received",
                "text": "Hi, how are you?"
            }
        ]
    }
    ```

    ### Возможные ответы:
    - **200 OK**: Возвращает информацию о пользователе и список сообщений между пользователями.
    - **404 NOT FOUND**: Возвращается, если указанный пользователь не найден.
    - **401 UNAUTHORIZED**: Возвращается, если токен авторизации недействителен или отсутствует.

    ### Ошибки:
    - **404**: "User not found" — если пользователь с таким `user_id` не существует.
    - **401**: "Unauthorized" — если токен авторизации отсутствует или недействителен.

    ### Заметки:
    - Сообщения классифицируются как отправленные (`sent`) или полученные (`received`) в зависимости от их отправителя.
    - Доступ к чату возможен только при авторизации текущего пользователя.

    """
    
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    db_messages = get_messages_by_user_ids(db, current_user.id, user.id)
    
    # Формируем список сообщений
    messages = []
    for message in db_messages:
        message_type = chat_schema.MessageType.SENT if message.sender_id == current_user.id else chat_schema.MessageType.RECEIVED
        messages.append(chat_schema.Message(type=message_type, text=message.text))
    
    return chat_schema.Chat(user=user, messages=messages)

@router.websocket("/{user_id}/ws")
async def chat_endpoint(websocket: WebSocket, user_id: int, access_token: str, db: orm.Session = Depends(get_db)):
    current_user = await get_user_by_token(db, access_token)
    user = get_user_by_id(db, user_id)
    
    await websocket.accept()                                    # Принимаем веб-сокет
    await manager.connect(current_user.username, websocket)     # Добавляем веб-сокет в менеджер и привязываем его к username текущего пользователя
    
    
    # Формируем событие подключения к чату текущего пользователя
    event = {
        "type": "joined",
        "sender": current_user.username,
        "receiver": user.username,
        "payload": {}
    }
    
    await redis.publish("chat", json.dumps(event))      # Публикуем событие в канал Redis
    await websocket.send_json(event)                    # Отправляем текущему пользователю событие

    try:
        while True:
            event = await websocket.receive_json()              # Ловим сообщение с веб-сокета
            
            await redis.publish("chat", json.dumps(event))      # Публикуем событие в канал Redis
            await websocket.send_json(event)                    # Отправляем текущему пользователю событие
            
            # Сохраняем сообщение в БД, если событие позволяет
            if event["type"] == "new_message":
                sender_id = current_user.id if current_user.username == event["sender"] else user.id
                receiver_id = current_user.id if current_user.username == event["receiver"] else user.id
                create_message(db, sender_id, receiver_id, event["payload"]["text"])
    except WebSocketDisconnect:
        manager.disconnect(current_user.username)               # Отключаем веб-сокет от менеджера
        
        # Формируем событие отключения от чата текущего пользователя
        event = {
            "type": "left",
            "sender": current_user.username,
            "receiver": user.username,
            "payload": {}
        }
        await redis.publish("chat", json.dumps(event))                      # Публикуем событие в канал Redis


async def redis_listener():
    pubsub = redis.pubsub()
    await pubsub.subscribe("chat")                                          # Подписываемся на публикацию в канал Redis

    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True)  # Ловаим события из канала Redis
        if message:
            await manager.send_message_to_receiver(message["data"])         # Отправляем событие в менеджер для дальнейшей пересылки клиентам
        await asyncio.sleep(0.1)
