import os
from typing import Optional, List, AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Field, Relationship

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# --- МОДЕЛИ ДАННЫХ (БЕЗ РОЛЕЙ) ---

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    username: str = Field(index=True) # Вернули username, если он был
    
    tasks: List["Task"] = Relationship(back_populates="owner")

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    status: str = Field(default="todo")
    priority: str = Field(default="medium")
    deadline: Optional[str] = Field(default=None, nullable=True) # Дедлайны оставляем
    
    # Связь с владельцем (создателем) задачи
    owner_id: int = Field(foreign_key="users.id") 
    owner: Optional["User"] = Relationship(back_populates="tasks")

# --- ФУНКЦИИ ИНИЦИАЛИЗАЦИИ ---

async def init_db():
    async with engine.begin() as conn:
        # Сначала УДАЛЯЕМ старую кривую структуру
        #await conn.run_sync(SQLModel.metadata.drop_all) 
        # Затем СОЗДАЕМ чистую новую
        await conn.run_sync(SQLModel.metadata.create_all)
    print("🚀 База SYNAPSE полностью пересоздана")

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session