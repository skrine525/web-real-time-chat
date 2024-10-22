import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine
from app.database.models import Base
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.chats import router as chats_router
from app.routers.chats import redis_listener as chats_redis_listener
from fastapi.middleware.cors import CORSMiddleware


# Lifespan для FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Добавляем слушатель Redis для отправки сообщений по веб-сокетам
    chat_redis = asyncio.create_task(chats_redis_listener())
    
    yield
    
    chat_redis.cancel()
    try:
        await chat_redis
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)        # Приложение FastAPI

# Отключаем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключаем роутеры
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(chats_router, prefix="/api")
