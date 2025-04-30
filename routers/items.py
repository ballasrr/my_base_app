from fastapi import APIRouter, HTTPException, status
from models.database import get_users, Base, engine, create_user, update_user, delete_user
from routers.models_items import UserUpdateRequest

router = APIRouter()


@router.on_event("startup")
async def startup():
    # Создание таблиц (в продакшене лучше использовать миграции)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@router.get("/users")
async def read_users():
    try:
        users = await get_users()
        return users
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/users")
async def add_user(name: str, email: str):
    try:
        user = await create_user(name, email)
        return {"id": user.id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/users/{user_id}", response_model=UserUpdateRequest)
async def update_user_endpoint(
    user_id: int,
    update_data: UserUpdateRequest,
):
    """
    Обновление данных пользователя

    - **user_id**: ID пользователя для обновления
    - **name** (опционально): новое имя
    - **email** (опционально): новый email
    """
    try:
        updated_user = await update_user(user_id=user_id,
                                         new_name=update_data.name,
                                         new_email=update_data.email)
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint_with_response(user_id: int):
    try:
        result = await delete_user(user_id)
        return result  # Вернет сообщение об успешном удалении
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
