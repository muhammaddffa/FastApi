from datetime import timedelta
from fastapi import HTTPException, status
from app.internal.repository.auth_repo import AuthRepository
from app.internal.util.auth import verify_password, create_access_token, verify_token
from app.dto.auth_dto import LoginRequestDTO, LoginResponseDTO, UserProfileDTO
from app.domain.user_model import User
from app.internal.config.settings import settings

class AuthService:
    def __init__(self, auth_repo: AuthRepository):
        self.auth_repo = auth_repo

    async def authenticate_user(self, login_data: LoginRequestDTO) -> LoginResponseDTO:
        # Cari user berdasarkan username atau email
        user = await self.auth_repo.get_user_by_username(login_data.username) \
            or await self.auth_repo.get_user_by_email(login_data.username)

        if not user or not verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        # Generate access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user.user_id,
                "username": user.username,
                "role": user.role.value,
                "employee_id": user.employee_id
            },
            expires_delta=access_token_expires
        )

        # Update last login
        await self.auth_repo.update_user_last_login(user.user_id)

        return LoginResponseDTO(
            access_token=access_token,
            token_type="bearer",
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role,
            employee_id=user.employee_id
        )

    async def get_current_user(self, token: str) -> User:
        payload = verify_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        user = await self.auth_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")

        return user

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
