from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, text, Connection, Column, Table, String, Integer, BigInteger, ForeignKey, select, inspect
from sqlalchemy.orm import registry, declarative_base, as_declarative, declared_attr, DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from models.config_db import *

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(bind=engine,
                                 class_=AsyncSession,
                                 expire_on_commit=False)
Base = declarative_base()


@as_declarative()
class AbstractModel:
    id = Column(Integer, autoincrement=True, primary_key=True)

    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class User(AbstractModel):
    __tablename__ = 'users'

    name = Column(String)
    email = Column(String)


class AddressModel(AbstractModel):
    __tablename__ = "addresses"
    emal = Column(String, nullable=False)
    user_id = Column(ForeignKey('users.id'))


async def create_user(name: str, email: str) -> User:
    """Асинхронное создание пользователя с валидацией и обработкой ошибок"""
    async with AsyncSessionLocal() as session:
        try:
            async with session.begin():
                # Проверяем, нет ли пользователя с таким email
                existing_user = await session.execute(
                    select(User).where(User.email == email))
                if existing_user.scalar_one_or_none() is not None:
                    raise ValueError(
                        f"Пользователь с email {email} уже существует")

                # Создаем нового пользователя
                user = User(name=name, email=email)
                session.add(user)

            # Возвращаем созданного пользователя с актуальными данными из БД
            async with session.begin():
                await session.refresh(user)
                return user

        except Exception as e:
            # Логируем ошибку (на практике используйте logging)
            print(f"Ошибка при создании пользователя: {str(e)}")
            raise  # Пробрасываем исключение дальше


async def get_users():
    """вернуть пользователей"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        return result.scalars().all()


async def update_user(user_id: int,
                      new_name: str = None,
                      new_email: str = None):
    """Обновление данных пользователя асинхронно"""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Получаем пользователя для обновления
            result = await session.execute(
                select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                raise ValueError(f"Пользователь с ID {user_id} не найден")

            # Обновляем только переданные поля
            if new_name is not None:
                user.name = new_name
            if new_email is not None:
                user.email = new_email

            # Сессия автоматически отслеживает изменения и сохранит их при commit
            session.add(user)

        # Проверяем обновленные данные
        async with session.begin():
            res = await session.execute(select(User).where(User.id == user_id))
            print(res.scalar())

    return user


async def delete_user(user_id: int):
    """Удаление пользователя асинхронно"""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Получаем пользователя для удаления
            result = await session.execute(
                select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                raise ValueError(f"Пользователь с ID {user_id} не найден")

            await session.delete(user)

        # Проверяем, что пользователь удален
        async with session.begin():
            res = await session.execute(select(User).where(User.id == user_id))
            if res.scalar() is not None:
                raise RuntimeError(
                    f"Пользователь с ID {user_id} не был удален")

    return {"message": f"Пользователь с ID {user_id} успешно удален"}
