import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# Импорты твоих модулей
from app.db.database import init_db
from app.router_auth import router as auth_router
from app.router import router as tasks_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # При запуске создаем таблицы
    # ВАЖНО: На продакшене (Render/Railway) таблицы создадутся сами при первом запуске
    await init_db()
    print("🚀 Synapse API: Database synced")
    yield

app = FastAPI(
    title="Synapse Kanban API",
    version="2.0.0",
    lifespan=lifespan
)

# --- НАСТРОЙКА CORS ---
# Берем адрес фронтенда из переменных окружения (для деплоя) или используем localhost
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    FRONTEND_URL, # Здесь будет твой адрес на Vercel
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ПОДКЛЮЧЕНИЕ РОУТЕРОВ ---
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Synapse API is running smoothly",
        "docs": "/docs"
    }