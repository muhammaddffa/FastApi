from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class Employee(BaseModel):
    employee_id: str
    employee_code: str
    full_name: str
    position: str
    departement: Optional[str] = None
    hire_date: datetime
    basic_salary: Decimal
    email: Optional[str] = None
    phone: Optional[str] = None
    bank_account: Optional[str] = None
    bank_name: Optional[str] = None
    is_active: Optional[bool] = True
    photo_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }