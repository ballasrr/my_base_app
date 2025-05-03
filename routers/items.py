from fastapi import APIRouter, HTTPException, status, Depends
from models.database import get_users,create_user, update_user, delete_user, create_item, update_item, delete_item, get_user_items, get_item, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession, engine
from typing import List, Optional
from routers.schemas import User, Item
from models.database import Base
router = APIRouter()

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Dependency для получения асинхронной сессии
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

# Эндпоинты для пользователей
@router.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    title: str,
    description: str,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Создание нового пользователя"""
    return await create_user(title=title, description=description, is_active=is_active)

@router.get("/users/{user_id}", response_model=Optional[User])
async def get_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение пользователя по ID"""
    user = await get_users(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=Optional[User])
async def update_user_endpoint(
    user_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """Обновление данных пользователя"""
    updated_user = await update_user(
        user_id=user_id,
        title=title,
        description=description,
        is_active=is_active
    )
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление пользователя по ID"""
    success = await delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None

# Эндпоинты для items
@router.post("/items/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item_endpoint(
    title: str,
    description: str,
    owner_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Создание нового item"""
    try:
        return await create_item(
            title=title,
            description=description,
            owner_id=owner_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users/{user_id}/items", response_model=List[Item])
async def get_user_items_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение всех items пользователя"""
    return await get_user_items(user_id)

@router.get("/items/{item_id}", response_model=Optional[Item])
async def get_item_endpoint(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение item по ID"""
    item = await get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/items/{item_id}", response_model=Optional[Item])
async def update_item_endpoint(
    item_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Обновление данных item"""
    updated_item = await update_item(
        item_id=item_id,
        title=title,
        description=description
    )
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item_endpoint(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление item по ID"""
    success = await delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return None
