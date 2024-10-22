from fastapi.routing import APIRouter
from fastapi import  Depends
from app.utils.auth import get_current_user
from app.schemas import chat as chat_schema
from app.schemas import user as user_schema
from sqlalchemy import orm
from app.database import get_db
from app.database.operations import get_user_by_id, create_message, get_messages_by_user_ids
from app.database import models
import asyncio, json
from redis.asyncio import Redis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.utils.auth import get_user_by_token
from sqlalchemy import orm
from app.database import get_db
from app.utils.connection_manager import ConnectionManager


router = APIRouter(prefix="/chats")
redis = Redis(host="chat_redis", db=1, decode_responses=True)
manager = ConnectionManager()


@router.get("", response_model=user_schema.UserList)
async def get_all_chats(current_user: user_schema.User = Depends(get_current_user), db: orm.Session = Depends(get_db)):
    users =  db.query(models.User).filter(models.User.username != current_user.username).all()
    return user_schema.UserList(users=users)

@router.get("/{user_id}", response_model=chat_schema.Chat)
async def get_chat(user_id, current_user: user_schema.User = Depends(get_current_user), db: orm.Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    db_messages = get_messages_by_user_ids(db, current_user.id, user.id)
    
    messages = []
    for message in db_messages:
        message_type = chat_schema.MessageType.SENT if message.sender_id == current_user.id else chat_schema.MessageType.RECEIVED
        messages.append(chat_schema.Message(type=message_type, text=message.text))
    
    return chat_schema.Chat(user=user, messages=messages)

@router.websocket("/{user_id}/ws")
async def chat_endpoint(websocket: WebSocket, user_id: int, access_token: str, db: orm.Session = Depends(get_db)):
    current_user = await get_user_by_token(db, access_token)
    user = get_user_by_id(db, user_id)
    
    await websocket.accept()
    await manager.connect(current_user.username, websocket)
    
    event = {
        "type": "joined",
        "sender": current_user.username,
        "receiver": user.username,
        "payload": {}
    }
    
    await redis.publish("chat", json.dumps(event))
    await websocket.send_json(event)

    try:
        while True:
            event = await websocket.receive_json()
            
            await redis.publish("chat", json.dumps(event))
            await websocket.send_json(event)
            
            # Сохраняем сообщение в БД, если событие позволяет
            if event["type"] == "new_message":
                sender_id = current_user.id if current_user.username == event["sender"] else user.id
                receiver_id = current_user.id if current_user.username == event["receiver"] else user.id
                create_message(db, sender_id, receiver_id, event["payload"]["text"])
    except WebSocketDisconnect:
        manager.disconnect(current_user.username)
        
        event = {
            "type": "left",
            "sender": current_user.username,
            "receiver": user.username,
            "payload": {}
        }
        await redis.publish("chat", json.dumps(event))


async def redis_listener():
    pubsub = redis.pubsub()
    await pubsub.subscribe("chat")

    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True)
        if message:
            await manager.send_message_to_receiver(message["data"])
        await asyncio.sleep(0.1)
