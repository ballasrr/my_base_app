from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, text, Connection, Column, Table, String, Integer, BigInteger, ForeignKey, select, inspect
from sqlalchemy.orm import registry, declarative_base, as_declarative, declared_attr, DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from models.config_db import *
from models.core import User, Item

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(bind=engine,
                                 class_=AsyncSession,
                                 expire_on_commit=False)
Base = declarative_base()



async def create_user(title: str, description: str, is_active: bool = True) -> User:
    async with AsyncSessionLocal() as session:
        try:
            user = User(title=title, description=description, is_active=is_active)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при создании пользователя: {str(e)}")
            raise


async def get_users(user_id: int) -> User | None:
    """Получение пользователя по ID"""
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
        except Exception as e:
            print(f"Ошибка при получении пользователя: {str(e)}")
            raise


async def update_user(user_id: int, title: str | None = None,
                     description: str | None = None,
                     is_active: bool | None = None) -> User | None:
    """Обновление данных пользователя"""
    async with AsyncSessionLocal() as session:
        try:
            async with session.begin():
                result = await session.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()

                if user is None:
                    return None

                if title is not None:
                    user.title = title
                if description is not None:
                    user.descrption = description
                if is_active is not None:
                    user.is_active = is_active

                session.add(user)
                await session.refresh(user)
                return user

        except Exception as e:
            print(f"Ошибка при обновлении пользователя: {str(e)}")
            raise


async def delete_user(user_id: int) -> bool:
    """Удаление пользователя по ID"""
    async with AsyncSessionLocal() as session:
        try:
            async with session.begin():
                result = await session.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()

                if user is None:
                    return False

                await session.delete(user)
                return True

        except Exception as e:
            print(f"Ошибка при удалении пользователя: {str(e)}")
            raise


async def create_item(title: str, description: str, owner_id: int) -> Item:
    """Создание нового item с привязкой к пользователю"""
    async with AsyncSessionLocal() as session:
        try:
            async with session.begin():
                # Проверяем существование пользователя
                user = await session.execute(select(User).where(User.id == owner_id))
                if user.scalar_one_or_none() is None:
                    raise ValueError(f"Пользователь с ID {owner_id} не существует")

                # Создаем новый item
                item = Item(title=title, description=description, owner_id=owner_id)
                session.add(item)

            async with session.begin():
                await session.refresh(item)
                return item

        except Exception as e:
            print(f"Ошибка при создании item: {str(e)}")
            raise


async def get_user_items(user_id: int) -> list[Item]:
    """Получение всех items пользователя"""
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Item).where(Item.owner_id == user_id))
            return list(result.scalars().all())
        except Exception as e:
            print(f"Ошибка при получении items пользователя: {str(e)}")
            raise


async def get_item(item_id: int) -> Item | None:
    """Получение item по ID"""
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Item).where(Item.id == item_id))
            return result.scalar_one_or_none()
        except Exception as e:
            print(f"Ошибка при получении item: {str(e)}")
            raise


async def update_item(item_id: int, title: str | None = None,
                     description: str | None = None) -> Item | None:
    """Обновление данных item"""
    async with AsyncSessionLocal() as session:
        try:
            async with session.begin():
                result = await session.execute(select(Item).where(Item.id == item_id))
                item = result.scalar_one_or_none()

                if item is None:
                    return None

                if title is not None:
                    item.title = title
                if description is not None:
                    item.description = description

                session.add(item)
                await session.refresh(item)
                return item

        except Exception as e:
            print(f"Ошибка при обновлении item: {str(e)}")
            raise


async def delete_item(item_id: int) -> bool:
    """Удаление item по ID"""
    async with AsyncSessionLocal() as session:
        try:
            async with session.begin():
                result = await session.execute(select(Item).where(Item.id == item_id))
                item = result.scalar_one_or_none()

                if item is None:
                    return False

                await session.delete(item)
                return True

        except Exception as e:
            print(f"Ошибка при удалении item: {str(e)}")
            raise
