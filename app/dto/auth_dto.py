from pydantic import BaseModel, Field
from typing import Optional
from domain.user_model import UserRole

class LoginRequestDTO(BaseModel):
    username: str =  Field (... , min_length=4, max_length=20)
    password: str =  Field (..., min_length=4, max_length=20)

class LoginResponseDTO(BaseModel):
    access_token: str
    token_type : str = "bearer"
    user_id: str
    usernmae: str
    email: str
    role: UserRole
    employee_id: Optional[str] = None

class UserProfileDTO(BaseModel):
    user_id: str
    username: str
    email: str
    role: UserRole
    employee_id: Optional[str]
    is_active: bool
    created_at: Optional[str]

