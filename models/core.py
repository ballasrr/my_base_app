
from sqlalchemy import create_engine, text, Connection, Column, Table, String, Integer, BigInteger, ForeignKey, select, inspect, Boolean
from sqlalchemy.orm import registry, declarative_base, as_declarative, declared_attr, DeclarativeBase, sessionmaker, relationship
from models.config_db import *

@as_declarative()
class AbstractModel:
    id = Column(Integer, autoincrement=True, primary_key=True)

    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

class User(AbstractModel):
    __tablename__ = "users"

    title = Column(String)
    description = Column(String)  # Исправлено с descrption на description
    is_active = Column(Boolean, default=True)

    # Правильное определение отношения один-ко-многим
    items = relationship("Item", back_populates="owner")

class Item(AbstractModel):
    __tablename__ = "items"

    title = Column(String)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Правильное определение обратного отношения
    owner = relationship("User", back_populates="items")
