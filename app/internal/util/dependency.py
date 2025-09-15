# app/internal/util/dependencies.py
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from app.internal.service.auth_service import AuthService
from app.internal.repository.auth_repo import AuthRepository
from app.internal.connection.prisma import get_db
from app.internal.util.auth import security
from app.domain.user_model import User
from prisma import Prisma

def get_auth_service(db: Prisma = Depends(get_db)) -> AuthService:
    auth_repo = AuthRepository(db)
    return AuthService(auth_repo)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    return await auth_service.get_current_user(credentials.credentials)