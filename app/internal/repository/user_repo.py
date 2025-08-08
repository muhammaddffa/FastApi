from app.internal.connection.prisma import prisma
from app.dto.user_dto import UserCreate, UserUpdate

async def get_all_users():
    return await prisma.user.find_many()

async def create_user(data: UserCreate):
    return await prisma.user.create(data=data.model_dump())
