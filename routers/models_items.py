from pydantic import BaseModel, EmailStr


class UserUpdateRequest(BaseModel):
    name: str | None = None
    email: str | None = None
