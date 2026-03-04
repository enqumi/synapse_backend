from sqlalchemy import select, delete
from app.db.database import Task, User, async_session
from app.schemas import STaskAdd, STaskUpdate
from typing import List, Optional

class TaskRepository:
    @classmethod
    async def add_one(cls, data: STaskAdd, owner_email: str) -> Optional[Task]:
        """
        Создает новую задачу и привязывает её к владельцу через email.
        """
        async with async_session() as session:
            # 1. Находим пользователя по email
            user_query = select(User).where(User.email == owner_email)
            result = await session.execute(user_query)
            user = result.scalar_one_or_none()
            
            if not user:
                return None 

            # 2. Превращаем схему в словарь и добавляем owner_id
            task_dict = data.model_dump()
            db_task = Task(**task_dict, owner_id=user.id)
            
            session.add(db_task)
            await session.commit()
            await session.refresh(db_task)
            return db_task

    @classmethod
    async def find_all(cls, user_email: str) -> List[Task]:
        """
        Возвращает все задачи, принадлежащие пользователю.
        """
        async with async_session() as session:
            # 1. Получаем пользователя
            user_query = select(User).where(User.email == user_email)
            user_res = await session.execute(user_query)
            user = user_res.scalar_one_or_none()
            
            if not user:
                return []

            # 2. Ищем его задачи
            query = select(Task).where(Task.owner_id == user.id)
            result = await session.execute(query)
            return list(result.scalars().all())

    @classmethod
    async def update_task(cls, task_id: int, task_data: STaskUpdate, user_email: str) -> bool:
        """
        Частично обновляет задачу. Идеально для перемещения (DND) и изменения сроков.
        """
        async with async_session() as session:
            # 1. Сначала находим пользователя, чтобы убедиться в правах доступа
            user_stmt = select(User).where(User.email == user_email)
            user_res = await session.execute(user_stmt)
            user = user_res.scalar_one_or_none()
            
            if not user:
                return False

            # 2. Ищем саму задачу, принадлежащую именно этому юзеру
            stmt = select(Task).where(Task.id == task_id, Task.owner_id == user.id)
            result = await session.execute(stmt)
            task = result.scalars().first()

            if not task:
                return False

            # 3. Обновляем только те поля, которые прислал фронтенд (exclude_unset=True)
            # Это критически важно для сохранения дедлайнов и описаний
            update_dict = task_data.model_dump(exclude_unset=True)

            for key, value in update_dict.items():
                setattr(task, key, value)

            await session.commit()
            return True

    @classmethod
    async def delete_task(cls, task_id: int, user_email: str) -> bool:
        """
        Удаляет задачу пользователя.
        """
        async with async_session() as session:
            user_query = select(User).where(User.email == user_email)
            user_res = await session.execute(user_query)
            user = user_res.scalar_one_or_none()

            if not user: 
                return False

            # Удаляем только если задача принадлежит юзеру
            query = delete(Task).where(
                Task.id == task_id, 
                Task.owner_id == user.id
            )
            result = await session.execute(query)
            await session.commit()
            
            # Если rowcount > 0, значит что-то было удалено
            return result.rowcount > 0