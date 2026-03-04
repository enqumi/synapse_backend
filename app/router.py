from fastapi import APIRouter, Depends, HTTPException
from app.repository import TaskRepository
from app.schemas import STaskAdd, STaskUpdate
from app.db.database import User
from app.core.auth_utils import get_current_user 

# Префикс /tasks
router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("")
async def get_tasks(current_user: str = Depends(get_current_user)):
    """Получение всех задач текущего пользователя"""
    # Исправлено: передаем current_user напрямую, так как это строка (email)
    return await TaskRepository.find_all(current_user)

@router.post("")
async def create_task(
    task_data: STaskAdd, 
    current_user: str = Depends(get_current_user)
):
    """Создание новой задачи"""
    # Исправлено: убрали .email
    new_task_id = await TaskRepository.add_one(task_data, current_user)
    if new_task_id is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return {"id": new_task_id, "status": "created"}

# В app/router.py

# Добавь PATCH в декоратор или просто проверь метод во фронтенде
@router.patch("/{task_id}")
@router.put("/{task_id}")
async def update_task(
    task_id: int, 
    task_data: STaskUpdate, # Проверь, что тут именно STaskUpdate!
    current_user: str = Depends(get_current_user)
):
    success = await TaskRepository.update_task(task_id, task_data, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return {"status": "success"}

@router.delete("/{task_id}")
async def delete_task(
    task_id: int, 
    current_user: str = Depends(get_current_user)
):
    """Удаление задачи"""
    # Исправлено: убрали .email
    success = await TaskRepository.delete_task(task_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Задача не найдена или нет прав")
    return {"status": "success"}