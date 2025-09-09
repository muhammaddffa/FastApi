from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from app.internal.repository.employee_repo import EmployeeRepository
from app.dto.employee_dto import (
    CreateEmployeeDto,
    UpdateEmployeeDto,
    EmployeeResponseDto,
    EmployeeListResponseDto,
    EmployeeQueryDto
)
from app.domain.employe_model import Employee

class EmployeeService:
    def __init__(self, employee_repo: EmployeeRepository):
        self.employee_repo = employee_repo

    # check if employee code already exists
    async def create_employee(self, employee_data: CreateEmployeeDto) -> EmployeeResponseDto:
        existing_code = await self.employee_repo.find_by_id(employee_data.employee_code)
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"employee with code '{employee_data.employee_code}' already exists"
            )
        
        # check if email already exists (if provided)
        if employee_data.email:
            existing_email = await self.employee_repo.find_by_email(employee_data.email)
        
            if existing_email:
                raise  HTTPException(
                    status_code= status.HTTP_400_BAD_REQUEST,
                    detail=f"employee with email '{employee_data.email}' already exists"
                )
            
            try:
                employee = await self.employee_repo.create(employee_data)
                return EmployeeResponseDto.model_validate(employee)
            except Exception as e:
                raise HTTPException(
                    status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create employe: {str(e)}"
                )
            
        
        