from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    EMPLOYEE = "employee"
    HRD = "hrd"
    FINANCE = "finance"
    ADMINISTRATOR = "administrator"

class User(BaseModel):
    user_id = str
    username = str
    email = str
    role = UserRole
    employee_id = Optional[str] = None
    is_active : bool = True
    created_at = Optional[datetime] = None
    updated_at = Optional[datetime] = None

class UserLogin(BaseModel): 
    username: str
    password: str

