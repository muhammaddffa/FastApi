from fastapi import Request, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
from internal.util.auth import verify_token
from internal.repository.auth_repo import AuthRepository
from internal.connection.prisma import get_db

class AuthMiddleware:
    def __init__(self):
        pass

    async def __call__(self, request: Request, call_next):
        # skip buat endpoint publicnya
        if request.url.path in ["/auth/login", "/docs", "/openapi.json","/health"]:
            response = await call_next(request)
            return response
        
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication headder is missing",
            )
        
        schema, token = get_authorization_scheme_param(authorization)
        if schema.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication schema",
            )
        try:
            payload = verify_token(token)
            request.state.use_id = payload.get("sub")
            request.state.username = payload.get("username")
            request.state.role = payload.get("role")
            request.state.employee_id = payload.get("employee_id")
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        
        response = await call_next(request)
        return response
    

        