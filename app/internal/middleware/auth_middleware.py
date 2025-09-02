from fastapi import Request, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
from internal.util.auth import verify_token
from internal.repository.auth_repo import AuthRepository
from internal.connection.prisma import get_db

