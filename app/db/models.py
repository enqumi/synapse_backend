from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    username: Optional[str] = None # Ты в JS использовал username, лучше добавить его
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Связь с задачами
    tasks: List["Task"] = Relationship(back_populates="owner") 

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False) # Мы на фронтенде используем 'name'
    description: Optional[str] = None
    status: str = Field(default="planned")
    priority: str = Field(default="medium")
    
    # ВОТ ОНО! Добавляем колонку в таблицу базы данных
    deadline: Optional[str] = Field(default=None, nullable=True)

    owner_id: int = Field(foreign_key="user.id", nullable=False)
    owner: Optional[User] = Relationship(back_populates="tasks")