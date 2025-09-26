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
        existing_code = await self.employee_repo.find_by_code(employee_data.employee_code)
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
    async def get_employee_by_id(self, employee_id: str) -> EmployeeResponseDto:
        employee = await self.employee_repo.find_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return EmployeeResponseDto.model_validate(employee)
    
    async def get_employees(self, query: EmployeeQueryDto) -> Dict[str, Any]:
        try:
            employess_data, total = await self.employee_repo.find_all(query)

            employees = [
                EmployeeListResponseDto.model_validate(emp)
                for emp in employess_data
            ]

            #pagination metadata
            total_pages = (total + query.limit - 1) // query.limit
            has_next = query.page < total_pages
            has_prev = query.page > 1

            return{
                "data": employees,
                "pagination": {
                    "current_page": query.page,
                    "total_pages": total_pages,
                    "total_items": total,
                    "items_per_page": query.limit,
                    "has_next": has_next,
                    "has_previous": has_prev
                }
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve employees: {str(e)}"
            )
    
    async def update_employee(self, employee_id: str, employee_data: UpdateEmployeeDto) -> EmployeeResponseDto:
        
        # checking employee exists
        existing_employee = await self.employee_repo.find_by_id(employee_id)
        if not existing_employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        #check email uniques
        if employee_data.email:
            existing_email = await self.employee_repo.find_by_email(employee_data.email)
            if existing_email and existing_email.employee_id != employee_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Employee with email '{employee_data.email}' already exists"
                )
            
        
        try:
            updated_employee = await self.employee_repo.update(employee_id, employee_data)
            if not updated_employee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No fields to updated"
                )
            
            return EmployeeResponseDto.model_validate(updated_employee)
        
        except Exception as e:
            if "Employee not found" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Employee not found"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"failed to update employee: {str(e)}"
            )
        
    async def delete_employee(self, employee_id:str, hard_delete: bool = False) -> dict[str, str]:
            employee = await self.employee_repo.find_by_id(employee_id)
            if not employee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Employee not found"
                )
            
            try:
                if hard_delete:
                    success = await self.employee_repo.hard_delete(employee_id)
                    action = "permanently deleted"
                else:
                    success = await self.employee_repo.soft_delete(employee_id)
                    action = "deactivated"
                
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to delete employee"
                    )
                
                return {
                    "message": f"Employee '{employee.full_name}' has been {action} successfully"
                }
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to delete employee: {str(e)}"
                )
            
    async def get_departments(self) -> List[str]:
        
        try:
            return await self.employee_repo.get_departments()
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch departments: {str(e)}"
            )
    
    async def get_employee_statistics(self) -> dict[str, int]:
        try:
            return await self.employee_repo.get_employee_count()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch employee statistics: {str(e)}"
            )
    
    async def search_employees(self, search_term: str, limit:int = 10) -> List[EmployeeListResponseDto]:
        query = EmployeeQueryDto(
            search=search_term,
            limit=limit,
            is_active=True
        )

        employees_data, _ = await self.employee_repo.find_all(query)
        return [EmployeeListResponseDto.model_validate(emp) for emp in employees_data]
                