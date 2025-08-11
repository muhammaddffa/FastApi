from app.internal.repository import user_repo
from app.dto.user_dto import UserCreate, UserUpdate
from fastapi import HTTPException

async def get_all_users_service():
    return await user_repo.get_all_users()

async def create_user_service(data: UserCreate):
    return await user_repo.create_user(data)

async def update_user_service(id: str, data: UserUpdate):
    return await user_repo.update_user(id, data)

async def get_user_by_id_service(id: str):
    return await user_repo.get_user_by_id(id)

async def delete_user_service(id: str):
    return await user_repo.delete_user(id)