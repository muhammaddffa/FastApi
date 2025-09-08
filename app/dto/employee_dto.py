from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator

class CreateEmployeeDto(BaseModel):
    employee_code: str = Field(..., min_length=1, max_length=20)
    full_name: str = Field(..., min_length=1, max_length=100)
    position: str = Field(..., min_length=1, max_length=100)
    departement: Optional[str] = Field(None, max_length=100)
    hire_date: datetime = Field(...)
    basic_salary: Decimal = Field(..., gt=0)
    email: Optional[EmailStr] = Field(None)
    phone: Optional[str] = Field(None, max_length=20)
    bank_account: Optional[str] = Field(None, max_length=30)
    bank_name: Optional[str] = Field(None, max_length=50)
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