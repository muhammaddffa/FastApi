from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, validator


class EmployeeStatusDto(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ON_LEAVE = "ON_LEAVE"
    SUSPENDED = "SUSPENDED"


class CreateEmployeeDto(BaseModel):
    employee_code: str = Field(..., min_length=1, max_length=20)
    full_name: str = Field(..., min_length=1, max_length=100)
    position: str = Field(..., min_length=1, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    hire_date: datetime = Field(...)
    basic_salary: Decimal = Field(..., gt=0)
    email: Optional[EmailStr] = Field(None)
    phone: Optional[str] = Field(None, max_length=20)
    bank_account: Optional[str] = Field(None, max_length=30)
    bank_name: Optional[str] = Field(None, max_length=50)
    status: Optional[EmployeeStatusDto] = Field(EmployeeStatusDto.ACTIVE    )   
    photo_url: Optional[str] = Field(None, max_length=235)

    @validator('employee_code')
    def validate_employee_code(cls, v):
        if not v.strip():
            raise ValueError("Employee code must be alphanumeric")
        return v.strip().upper()
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if not v.strip():
            raise ValueError("Full name must be alphanumeric")
        return v.strip().title()
    

class UpdateEmployeeDto(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    position: Optional[str] = Field(None, min_length=1, max_length=100)
    department: Optional[str] = Field(None, max_length=50)
    basic_salary: Optional[Decimal] = Field(None, gt=0)
    email: Optional[EmailStr] = Field(None)
    phone: Optional[str] = Field(None, max_length=20)
    bank_account: Optional[str] = Field(None, max_length=30)
    bank_name: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    photo_url: Optional[str] = Field(None, max_length=235)

    @validator('full_name')
    def validate_full_name(cls, v):
        if not v.strip():
            raise ValueError("Full name cannot be empty")
        return v.strip().title() if v else v
    
    class Config: 
        json_encoders = {
            Decimal: lambda v: float(v)
        }

class EmployeeResponseDto(BaseModel):
    employee_id: str
    employee_code: str
    full_name: str
    position: str
    department: Optional[str]
    hire_date: datetime
    basic_salary: Decimal
    email: Optional[str]
    phone: Optional[str] 
    bank_account: Optional[str]
    bank_name: Optional[str] 
    status: EmployeeStatusDto
    is_active: bool
    photo_url: Optional[str]
    created_at: datetime
    updated_at: datetime

class EmployeeListResponseDto(BaseModel):
    employee_id: str
    employee_code: str
    full_name: str
    position: str
    department: Optional[str]
    status: EmployeeStatusDto
    is_active: bool
    basic_salary: Decimal

    class Config:
        from_attributes = True 
        json_encoders = {
            Decimal: lambda v: float(v)
        }

class EmployeeQueryDto(BaseModel):
    page: int = Field(1, ge=1, description="Number of page")
    limit: int = Field(10, ge=1, le=100)
    search: Optional[str] = Field(None)
    department: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)
    sort_by: Optional[str] = Field("full_name")
    sort_order: Optional[str] = Field("asc", pattern="^(asc|desc)$")

    class Config: 
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }