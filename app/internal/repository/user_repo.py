from app.internal.connection.prisma import prisma
from app.dto.user_dto import UserCreate, UserUpdate

async def get_all_users():
    return await prisma.user.find_many()

async def create_user(data: UserCreate):
    return await prisma.user.create(data=data.model_dump())

async def update_user(id: str, data: UserUpdate):
    return await prisma.user.update(where={"id": id}, data=data.model_dump(exclude_unset=True))

async def get_user_by_id(id:str):
    return await prisma.user.find_unique(where={"id": id})

async def delete_user(id: str):
    return await prisma.user.delete(where={"id": id})