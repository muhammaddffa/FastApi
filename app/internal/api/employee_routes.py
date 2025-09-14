from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer

from app.internal.connection.prisma import get_prisma
from app.internal.repository.employee_repo import EmployeeRepository
from app.internal.service.employee_service import EmployeeService
from app.internal.util.auth import get_current_user
from app.internal.util.rbac import rbac_required
from app.internal.util.response import success_response, error_response
from app.dto.employee_dto import (
    CreateEmployeeDto, 
    UpdateEmployeeDto, 
    EmployeeResponseDto, 
    EmployeeListResponseDto,
    EmployeeQueryDto
)
from app.domain.user_model import User

router = APIRouter(prefix="/api/employee", tags=["Employee"])
security = HTTPBearer()

def get_employee_service():
    prisma = get_prisma()
    employee_repo = EmployeeRepository(prisma)
    return EmployeeService(employee_repo)

@router.post(
    "",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee",
    description="Create a new employee record, requires HR or Finance role"
)

@rbac_required(["hrd", "finance"])
async def create_employee(
    employee_data: CreateEmployeeDto,
    current_user: User = Depends(get_current_user),
    employee_service: EmployeeService = Depends(get_employee_service)
):
    try: 
        employee = await employee_service.create_employee(employee_data)
        return success_response(
            data=employee.model_dump(),
            message="Employee created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message="Internal server error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

@router.get(
    "",
    response_model= Dict[str, Any],
    summary="Get all Employees",
    description="Get all employees, requires HR or Finance role"
)
@rbac_required(["hrd", "finance"])
async def get_employees(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str = Query(None),
    department: str = Query(None),
    is_active: bool = Query(None),
    sort_by: str = Query("full_name"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    employee_service: EmployeeService = Depends(get_employee_service)
):
    try:
        query = EmployeeQueryDto(
            page=page,
            limit=limit,
            search=search,
            department=department,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order
        )

        result = await employee_service.get_employees(query)
        return success_response(
            data = result["data"],
            message="Employees fetched successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message="Internal server error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@router.get(
    "/search",
    response_model=Dict[str, Any],
    summary="Quick search employees",
    description="Quick search employees by name, code, or position"
)
@rbac_required(["hrd", "finance"])
async def search_employees(
    q: str = Query(..., min_length=1, description="Search term"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
    current_user: User = Depends(get_current_user),
    employee_service: EmployeeService = Depends(get_employee_service)
):
    try:
        employees = await employee_service.search_employees(q, limit)
        return success_response(
            data = [emp.model_dump() for emp in employees],
            message=f"Found {len(employees)} employees"
        )
    except Exception as e:
        return error_response(
            message="Search failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
