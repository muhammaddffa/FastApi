from typing import Optional
from prisma import Prisma
from domain.user_model import User
from datetime import datetime

class AuthRepository:
    def __init__(self, db: Prisma):
        self.db = db

    async def get_user_by_username(self, username: str) -> Optional[User]:
        user = await self.db.users.find_unique(where={"username": username})
        if user: 
            return User(**user.dict())
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        user = await self.db.users.find_unique(where={"email": email})
        if user: 
            return User(**user.dict())
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        user = await self.db.users.find_unique(where={"user_id": user_id})
        if user: 
            return User(**user.dict())
        return None
    
    async def update_user_last_login(self, user_id: str):
        return await self.db.users.update(
            where={"user_id": user_id}, 
            data={"updated_at": datetime.utcnow()
            }
        )