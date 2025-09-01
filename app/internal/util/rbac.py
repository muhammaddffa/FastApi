from typing import List, Dict
from fastapi import HTTPException, status
from domain.user_model import UserRole

class RolePermissions:
    PERMISSIONS = {
        UserRole.EMPLOYEE: [
            "view_own_profile",
            "edit_own_payslip",
            "view_own_attendance",
            "update_own_profile",
        ],
        UserRole.HRD: [
            "view_own_profile",
            "edit_own_payslip",
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
        UserRole.ADMINISTRATOR: ["view_own_profile",
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
    def require_permission(cls, permission: str):
        def decarator(func):
            def wrapper(*args, **kwargs):
                current_user = kwargs.get('current_user')
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required",
                    )
                if not cls.has_permission(current_user.role, permission):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions. Required {permission}",
                    )
                return func(*args, **kwargs)
            return wrapper
        return decarator