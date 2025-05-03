from pydantic import BaseModel
from typing import Optional, List

class UserBase(BaseModel):
    title: str
    description: str
    is_active: bool = True

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        from_attributes = True  # Ранее называлось orm_mode=True

class ItemBase(BaseModel):
    title: str
    description: str
    owner_id: int

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    class Config:
        from_attributes = True
