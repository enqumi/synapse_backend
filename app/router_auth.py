from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlmodel import select, or_
from app.db.database import get_session, User
from app.core.auth_utils import hash_password, verify_password, create_access_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.get("/test-auth")
async def test_auth(token: str = Depends(oauth2_scheme)):
    return {"message": "Кнопка Authorize теперь точно есть!"}

@router.post("/register")
async def register(user_data: User, session: AsyncSession = Depends(get_session)):
    statement = select(User).where(User.email == user_data.email)
    result = await session.execute(statement)
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже занят")

    # 2. Хешируем пароль
    user_data.hashed_password = hash_password(user_data.hashed_password)
    
    # 3. Обнуляем ID, чтобы PostgreSQL сам его сгенерировал (serial)
    user_data.id = None 
    
    session.add(user_data)
    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка БД: {str(e)}")
        
    return {"status": "success", "message": "Пользователь создан"}

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: AsyncSession = Depends(get_session)
):
    # Теперь ищем И по email, И по username
    statement = select(User).where(
        or_(
            User.email == form_data.username, 
            User.username == form_data.username
        )
    )
    result = await session.execute(statement)
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверный логин или пароль")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}