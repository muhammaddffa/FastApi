from datetime import timedelta
from fastapi import HTTPException, status
from app.internal.repository.auth_repo import AuthRepository
from app.internal.util.auth import verify_password, create_access_token, verify_token
from app.dto.auth_dto import LoginRequestDTO, LoginResponseDTO, UserProfileDTO
from app.domain.user_model import User
from app.internal.config.settings import settings
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, auth_repo: AuthRepository):
        self.auth_repo = auth_repo

    async def authenticate_user(self, login_data: LoginRequestDTO) -> LoginResponseDTO:
        logger.info(f"Starting authentication for username: {login_data.username}")
        
        try:
            # Cari user berdasarkan username
            logger.debug(f"Searching user by username: {login_data.username}")
            user = await self.auth_repo.get_user_by_username(login_data.username)
            
            if not user:
                logger.debug(f"User not found by username, trying email: {login_data.username}")
                user = await self.auth_repo.get_user_by_email(login_data.username)

            # Jika user tidak ditemukan
            if not user:
                logger.warning(f"User not found: {login_data.username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password"
                )

            logger.info(f"User found: {user.username}, role: {user.role}, active: {user.is_active}")

            # Check if user is active
            if not user.is_active:
                logger.warning(f"User is inactive: {user.username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is inactive"
                )

            # Log password verification attempt
            logger.debug(f"Verifying password for user: {user.username}")
            logger.debug(f"Plain password length: {len(login_data.password)}")
            logger.debug(f"Hashed password from DB: {user.password[:50]}...")  # Only log first 50 chars
            
            # Verify password
            password_valid = verify_password(login_data.password, user.password)
            logger.debug(f"Password verification result: {password_valid}")
            
            if not password_valid:
                logger.warning(f"Invalid password for user: {user.username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password"
                )

            logger.info(f"Authentication successful for user: {user.username}")

            # Generate access token
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            token_data = {
                "sub": user.user_id,
                "username": user.username,
                "role": user.role.value,
                "employee_id": user.employee_id
            }
            
            logger.debug(f"Creating token with data: {token_data}")
            access_token = create_access_token(
                data=token_data,
                expires_delta=access_token_expires
            )

            # Update last login
            await self.auth_repo.update_user_last_login(user.user_id)
            logger.info(f"Updated last login for user: {user.username}")

            response = LoginResponseDTO(
                access_token=access_token,
                token_type="bearer",
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                role=user.role,
                employee_id=user.employee_id
            )
            
            logger.info(f"Login response created successfully for user: {user.username}")
            return response

        except HTTPException as he:
            logger.error(f"HTTP Exception during authentication: {he.detail}")
            raise he
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Authentication service error: {str(e)}"
            )

    async def get_current_user(self, token: str) -> User:
        logger.debug(f"Getting current user from token")
        
        try:
            payload = verify_token(token)
            user_id = payload.get("sub")

            if not user_id:
                logger.warning("No user_id found in token payload")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

            user = await self.auth_repo.get_user_by_id(user_id)
            if not user:
                logger.warning(f"User not found for user_id: {user_id}")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
            
            if not user.is_active:
                logger.warning(f"User is inactive: {user.username}")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")

            logger.debug(f"Current user retrieved successfully: {user.username}")
            return user
            
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.error(f"Error getting current user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token validation failed"
            )

    async def get_user_profile(self, user_id: str) -> UserProfileDTO:
        user = await self.auth_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return UserProfileDTO(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role,
            employee_id=user.employee_id,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None,
        )