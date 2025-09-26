from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer

from app.internal.connection.prisma import get_db
from app.internal.repository.employee_repo import EmployeeRepository
from app.internal.service.employee_service import EmployeeService
from app.internal.util.rbac import require_permission
from app.internal.util.response import success_response, error_response
from app.dto.employee_dto import (
    CreateEmployeeDto, 
    UpdateEmployeeDto, 
    EmployeeResponseDto, 
    EmployeeListResponseDto,
    EmployeeQueryDto
)
from app.internal.util.dependency import get_current_user
from app.domain.user_model import User
from prisma import Prisma


router = APIRouter(prefix="/api/employee", tags=["Employee"])
security = HTTPBearer()

def get_employee_service(db: Prisma = Depends(get_db)) -> EmployeeService:
    employee_repo = EmployeeRepository(db)
    return EmployeeService(employee_repo)

# Create Employee
@router.post(
    "",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee",
    description="Create a new employee record, requires HR or Finance role"
)

@require_permission(["hrd", "finance"])
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

# Update Employee
@router.patch(
    "/{employee_id}",
    response_model=Dict[str,Any],
    description="Update employee data, requires HR or Finance role"
)
@require_permission(["hrd", "finance"])
async def update_employee(
    employee_id: str,
    employee_data: UpdateEmployeeDto,
    current_user: User = Depends(get_current_user),
    employee_service: EmployeeService = Depends(get_employee_service)
):
    try:
        employee = await employee_service.update_employee(employee_id, employee_data)
        return success_response(
            data=employee.model_dump(),
            message="Employee updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message="Failed to update employee",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get(
    "",
    response_model= Dict[str, Any],
    summary="Get all Employees",
    description="Get all employees, requires HR or Finance role"
)
@require_permission(["hrd", "finance"])
async def get_employees(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: str = Query(None),
    department: str = Query(None),
    is_active: bool = Query(None),
    sort_by: str = Query("full_name"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
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
@require_permission(["hrd", "finance"])
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
    
@router.get(
    "/departments",
    response_model=Dict[str, Any],
    summary="Get All Departments",
    description="Get list of all unique departments"
)
@require_permission(["hrd", "finance"])
async def get_departments(
    current_user: User = Depends(get_current_user),
    employee_service: EmployeeService = Depends(get_employee_service)
):
    
    try:
        departments = await employee_service.get_departments()
        return success_response(
            data=departments,
            message="Departments fetched successfully"
        )
    except Exception as e:
        return error_response(
            message="Failed to fetch departments",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

@router.get(
    "/statistics",
    response_model=Dict[str, Any],
    summary="Get employee statistics",
    description="Get employee count statistics"
)
@require_permission(["hrd", "finance"])
async def get_employee_statistics(
    current_user: User = Depends(get_current_user),
    employee_service: EmployeeService = Depends(get_employee_service)
):
    try:
        stats = await employee_service.get_employee_statistics()
        return success_response(
            data=stats,
            message="Employee statistics fetched successfully"
        )
    except Exception as e:
        return error_response(
            message="Failed to fetch employee statistics",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@router.get(
    "/me",
    response_model=Dict[str, Any],
    summary="Get my Profile",
    description="Get current employee's profile information"
)
@require_permission(["employee"])
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    employee_service: EmployeeService = Depends(get_employee_service)
):
    try:
        if not current_user.employee_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee profile not found"
            )
        
        employee = await employee_service.get_employee_by_id(current_user.employee_id)
        return success_response(
            data= employee.model_dump(),
            message= "Profile fetched successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message="Failed to fetch profile",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

@router.get(
    "/{employee_id}",
    response_model=Dict[str, Any],
    summary="Get employee by ID",
    description="Get employee by ID, requires HR or Finance role"
)
@require_permission(["hrd", "finance"])
async def get_employee_by_id(
    employee_id: str,
    current_user: User = Depends(get_current_user),
    employee_service: EmployeeService = Depends(get_employee_service)
):
    try:
        employee = await employee_service.get_employee_by_id(employee_id)
        return success_response(
            data= employee.model_dump(),
            message= "Employee fetched successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message="Failed to fetch employee",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

@router.delete(
    "/{employee_id}",
    response_model=Dict[str, Any],
    summary="Delete employee",
    description="Delete employee employee (deactivate)"
)
@require_permission(["hrd"])
async def deleted_employee(
    employee_id: str,
    hard_delete: bool = Query(False, description="Permanent delete if true"),
    current_user: User = Depends(get_current_user),
    employee_service: EmployeeService = Depends(get_employee_service)
):
    try:
        result = await employee_service.delete_employee(employee_id, hard_delete)
        return success_response(
            data= None,
            message=result["message"]
        )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message="Failed to delete employee",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

