from typing import List, Dict
from functools import wraps
from fastapi import HTTPException, status
from app.domain.user_model import UserRole

class RolePermissions:
    PERMISSIONS = {
        UserRole.EMPLOYEE: [
            "employee", 
            "view_own_profile",
            "view_own_payslip",  
            "view_own_attendance",
            "update_own_profile",
        ],
        UserRole.HRD: [
            "hrd",  
            "view_own_profile",
            "view_own_payslip",
            "view_own_attendance",
            "update_own_profile",
            "view_all_employees",
            "create_employee",
            "update_employee",
            "view_all_attendance",
            "manage_attendance",
            "view_payroll_periods",
            "create_payroll_periods"
        ],
        UserRole.FINANCE: [
            "finance",  
            "view_own_profile",
            "view_own_payslip",
            "view_own_attendance", 
            "update_own_profile",
            "view_all_employees",
            "view_all_payslips",
            "create_payslip",
            "update_payslip",
            "approve_payslip",
            "view_payroll_periods",
            "create_payroll_periods",
            "manage_allowances",
            "manage_deductions",
            "export_payroll"
        ],
        UserRole.ADMINISTRATOR: [
            "administrator",  
            "view_own_profile",
            "view_own_payslip",
            "view_own_attendance",
            "update_own_profile",
            "view_all_employees",
            "create_employee", 
            "update_employee",
            "delete_employee",
            "view_all_attendance",
            "manage_attendance",
            "view_all_payslips",
            "create_payslip",
            "update_payslip",
            "approve_payslip",
            "delete_payslip",
            "view_payroll_periods",
            "create_payroll_periods",
            "update_payroll_periods",
            "delete_payroll_periods",
            "manage_allowances",
            "manage_deductions",
            "export_payroll",
            "manage_users",
            "view_export_logs"
        ],
    }

    @classmethod
    def has_permission(cls, user_role: UserRole, permission: str) -> bool:
        return permission in cls.PERMISSIONS.get(user_role, [])
    
    @classmethod
    def require_permission(cls, permissions: List[str]):
        def decorator(func):
            @wraps(func)  # ✅ Fixed: Added @wraps for proper metadata preservation
            async def wrapper(*args, **kwargs):
                # ✅ Fixed: Better way to get current_user from kwargs
                current_user = None
                for key, value in kwargs.items():
                    if hasattr(value, 'role') and hasattr(value, 'user_id'):
                        current_user = value
                        break
                
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                # Check if user has any of the required permissions
                has_access = any(
                    cls.has_permission(current_user.role, permission) 
                    for permission in permissions
                )
                
                if not has_access:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions. Required one of: {', '.join(permissions)}",
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator

# Fungsi standalone untuk backward compatibility
def require_permission(permissions: List[str]):
    return RolePermissions.require_permission(permissions)