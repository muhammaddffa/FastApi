from typing import Optional
from datetime import datetime
from prisma import Prisma
from app.domain.user_model import User, UserRole
import logging

logger = logging.getLogger(__name__)

class AuthRepository:
    def __init__(self, db: Prisma):
        self.db = db

    async def get_user_by_username(self, username: str) -> Optional[User]:
        try:
            logger.debug(f"Searching user by username: {username}")
            user_data = await self.db.users.find_unique(where={"username": username})
            
            if user_data:
                logger.debug(f"User found by username: {user_data.username}, role: {user_data.role}")
                # Convert role string to UserRole enum
                user_dict = user_data.dict()
                user_dict['role'] = UserRole(user_dict['role'])
                user = User(**user_dict)
                logger.debug(f"User object created successfully for: {user.username}")
                return user
            else:
                logger.debug(f"No user found with username: {username}")
                return None
                
        except Exception as e:
            logger.error(f"Error searching user by username {username}: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        try:
            logger.debug(f"Searching user by email: {email}")
            user_data = await self.db.users.find_unique(where={"email": email})
            
            if user_data:
                logger.debug(f"User found by email: {user_data.username}, role: {user_data.role}")

                user_dict = user_data.dict()
                user_dict['role'] = UserRole(user_dict['role'])
                user = User(**user_dict)
                logger.debug(f"User object created successfully for: {user.username}")
                return user
            else:
                logger.debug(f"No user found with email: {email}")
                return None
                
        except Exception as e:
            logger.error(f"Error searching user by email {email}: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        try:
            logger.debug(f"Searching user by ID: {user_id}")
            user_data = await self.db.users.find_unique(where={"user_id": user_id})
            
            if user_data:
                logger.debug(f"User found by ID: {user_data.username}, role: {user_data.role}")

                user_dict = user_data.dict()
                user_dict['role'] = UserRole(user_dict['role'])
                user = User(**user_dict)
                logger.debug(f"User object created successfully for: {user.username}")
                return user
            else:
                logger.debug(f"No user found with ID: {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error searching user by ID {user_id}: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    async def update_user_last_login(self, user_id: str):
        try:
            logger.debug(f"Updating last login for user ID: {user_id}")
            result = await self.db.users.update(
                where={"user_id": user_id},
                data={"updated_at": datetime.utcnow()}
            )
            logger.debug(f"Last login updated successfully for user: {result.username}")
            return result
        except Exception as e:
            logger.error(f"Error updating last login for user {user_id}: {str(e)}")
            raise e