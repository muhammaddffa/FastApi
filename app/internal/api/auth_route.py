from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from internal.service.auth_service import AuthService
from internal.repository.auth_repo import AuthRepository
from internal.connection.prisma import get_db
from internal.util.auth import security
from internal.util.rbac import RolePermissions
from dto.auth_dto import LoginRequestDTO, LoginResponseDTO, UserProfileDTO
from dto.response_dto import ResponseDTO
from domain.user_model import User, UserRole
from prisma import Prisma

router = APIRouter(prefix="/api/auth", tags=["Auth"])

def get_auth_service(db: Prisma = Depends(get_db)) -> AuthService:
    auth_repo = AuthRepository(db)
    return AuthService(auth_repo)

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        auth_service: AuthService = Depends(get_auth_service)
) -> User:
    return await auth_service.get_current_user(credentials.credentials)

def require_role (*allowed_roles):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user= kwargs.get('current_user')
            if not current_user or current_user not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No permission for this role"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@router.post("/login", response_model=ResponseDTO[LoginResponseDTO])
async def login(
    login_data: LoginRequestDTO,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        result = await auth_service.authenticate_user(login_data)
        return ResponseDTO[LoginResponseDTO](
            success=True,
            message="Login successful",
            data=result,
            error=None
        )
    except Exception as e:
        return ResponseDTO[LoginResponseDTO](
            success=False,
            message="Login failed",
            error=str(e)
        )

@router.get("/profile", response_model=ResponseDTO[UserProfileDTO])
async def get_profile(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        profile = await auth_service.get_user_profile(current_user.user_id) 
        return ResponseDTO[UserProfileDTO](
            success=True,
            message= "Profile retrieved successfully",
            data= profile,
        )
    except Exception as e:
        return ResponseDTO[UserProfileDTO](
            success=False,
            message="Failed to retrieve profile",
            error=str(e)
        )
    
@router.get("verify", response_model=ResponseDTO[UserProfileDTO])
async def verify_token(
    current_user: User = Depends(get_current_user)
):
    return ResponseDTO[UserProfileDTO](
        success=True,
        message= "Token is valid",
        data= UserProfileDTO(
            user_id = current_user.user_id,
            username= current_user.username,
            email= current_user.email,
            role= current_user.role,
            employee_id=current_user.employee_id,
            is_active=current_user.is_active,
            created_at= current_user.created_at.isoformat() if current_user.created_at else None
        )
    )

#route roles

@router.get("/admin/users", response_model=ResponseDTO[list])
@require_role(UserRole.ADMINISTRATOR)
async def get_all_users(
    current_user: User = Depends(get_current_user)
):
    return ResponseDTO[list](
        success= True,
        message= "User retrieved successfully",
        data= []
    )

@router.get("/hrd/employess", response_model=ResponseDTO[list])
@require_role(UserRole.HRD, UserRole.ADMINISTRATOR)
async def get_all_employees(
    current_user: User = Depends(get_all_employees)
):
    return ResponseDTO[list](
        success= True,
        message= "Employees retrieved successfully",
        data= []
    )

@router.get("/finance/payslips", response_model=ResponseDTO[list])
@require_role(UserRole.FINANCE, UserRole.ADMINISTRATOR)
async def get_all_payslips(
    current_user: User = Depends(get_current_user)
):
    return ResponseDTO[list](
        success= True,
        message= "Payslips retrieved successfully",
        data= []
    )

