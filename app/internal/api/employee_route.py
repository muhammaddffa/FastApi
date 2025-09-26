from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Form, File, UploadFile
from fastapi.security import HTTPBearer

from app.internal.connection.prisma import get_db
from app.internal.repository.employee_repo import EmployeeRepository
from app.internal.service.cloudinary_service import CloudinaryService
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
from datetime import datetime
from decimal import Decimal

router = APIRouter(prefix="/api/employee", tags=["Employee"])
security = HTTPBearer()

def get_employee_service(db: Prisma = Depends(get_db)) -> EmployeeService:
    employee_repo = EmployeeRepository(db)
    cloudinary_service = CloudinaryService()
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
    # Required form fields
    employee_code: str = Form(...),
    full_name: str = Form(...),
    position: str = Form(...),
    hire_date: str = Form(..., description="ISO format: YYYY-MM-DD"),
    basic_salary: float = Form(...),
    
    # Optional form fields
    department: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    bank_account: Optional[str] = Form(None),
    bank_name: Optional[str] = Form(None),
    status: str = Form("ACTIVE"),
    
    # Optional photo upload
    photo: Optional[UploadFile] = File(None),
    
    # Dependencies
    current_user: User = Depends(get_current_user),
    employee_service: EmployeeService = Depends(get_employee_service)
):
   
    try:
        # Parse and validate form data
        employee_data = CreateEmployeeDto(
            employee_code=employee_code,
            full_name=full_name,
            position=position,
            department=department,
            hire_date=datetime.fromisoformat(hire_date),
            basic_salary=Decimal(str(basic_salary)),
            email=email,
            phone=phone,
            bank_account=bank_account,
            bank_name=bank_name,
            status=status
        )
        
        # Create employee
        employee = await employee_service.create_employee(employee_data)
        
        # Handle photo upload if provided
        if photo:
            update_data = UpdateEmployeeDto()
            updated_employee = await employee_service.update_employee(
                employee.employee_id, 
                update_data, 
                photo
            )
            return success_response(
                data=updated_employee.model_dump() if hasattr(updated_employee, 'model_dump') else updated_employee,
                message="Employee created with photo successfully"
            )
        
        return success_response(
            data=employee.model_dump(),
            message="Employee created successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data format: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=f"Failed to create employee: {str(e)}",
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
    
# Update Employee
@router.patch(
    "/{employee_id}",
    response_model=Dict[str, Any],
    summary="Update employee",
    description="Update employee with form data and optional photo upload"
)
@require_permission(["hrd", "finance"])
async def update_employee(
    employee_id: str,
    
    # Optional form fields for update
    full_name: Optional[str] = Form(None),
    position: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    basic_salary: Optional[float] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    bank_account: Optional[str] = Form(None),
    bank_name: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    
    # Optional photo upload
    photo: Optional[UploadFile] = File(None),
    
    # Dependencies
    current_user: User = Depends(get_current_user),
    employee_service: EmployeeService = Depends(get_employee_service)
):
    try:
        # Build update data from provided form fields
        update_fields = {}
        
        if full_name is not None:
            update_fields['full_name'] = full_name
        if position is not None:
            update_fields['position'] = position
        if department is not None:
            update_fields['department'] = department
        if basic_salary is not None:
            update_fields['basic_salary'] = Decimal(str(basic_salary))
        if email is not None:
            update_fields['email'] = email
        if phone is not None:
            update_fields['phone'] = phone
        if bank_account is not None:
            update_fields['bank_account'] = bank_account
        if bank_name is not None:
            update_fields['bank_name'] = bank_name
        if status is not None:
            update_fields['status'] = status
        if is_active is not None:
            update_fields['is_active'] = is_active
        
        # Check if any fields provided for update
        if not update_fields and not photo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        # Create UpdateEmployeeDto with only provided fields
        employee_data = UpdateEmployeeDto(**update_fields)
        
        # Update employee with optional photo
        updated_employee = await employee_service.update_employee(
            employee_id, 
            employee_data, 
            photo
        )
        
        photo_message = " with photo" if photo else ""
        return success_response(
            data=updated_employee.model_dump() if hasattr(updated_employee, 'model_dump') else updated_employee,
            message=f"Employee updated{photo_message} successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data format: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        return error_response(
            message=f"Failed to update employee: {str(e)}",
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

