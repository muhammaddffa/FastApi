from datetime import datetime
from typing import Optional, List, Tuple
from prisma.models import employees
from prisma import Prisma
from app.dto.employee_dto import CreateEmployeeDto, UpdateEmployeeDto, EmployeeQueryDto

class EmployeeRepository:
    def __init__(self, db: Prisma):
        self.prisma = db
        
    
    async def create(self, employee_data: CreateEmployeeDto) -> employees:
        return await self.prisma.employees.create(
            data= {
                "employee_code": employee_data.employee_code,
                "full_name": employee_data.full_name,
                "position": employee_data.position,
                "department": employee_data.department,
                "hire_date": employee_data.hire_date,
                "basic_salary": employee_data.basic_salary,
                "email": employee_data.email,
                "phone": employee_data.phone,
                "bank_account": employee_data.bank_account,
                "bank_name": employee_data.bank_name,
                "status": employee_data.status,
                "photo_url": employee_data.photo_url
            }
        )
    
    async def find_by_id(self, employee_id: str) -> Optional[employees]:
        return await self.prisma.employees.find_unique(
            where={
                "employee_id": employee_id   
                }
            )
    
    async def find_by_code(self, employee_code: str) -> Optional[employees]:
        return await self.prisma.employees.find_unique(
            where={
                "employee_code": employee_code   
                }
            )
    async def find_by_email(self, email: str) -> Optional[employees]:
        return await self.prisma.employees.find_first(
            where={
                "email": email
                }
            )
    async def find_all(self, query: EmployeeQueryDto) -> Tuple[List[employees], int]:
        
        where = {}

        if query.search:
            where["OR"] = [
                {"full_name": {"contains": query.search, "mode": "insensitive"}},
                {"employee_code": {"contains": query.search, "mode": "insensitive"}},
                {"position": {"contains": query.search, "mode": "insensitive"}},
            ]
        
        if query.department:
            where["department"] = {"contains": query.department, "mode": "insensitive"}

        if query.is_active is not None:
            where["is_active"] = query.is_active

        # build order by
        order = {}
        if query.sort_by:
            order[query.sort_by] = query.sort_order

        # calculate offset
        offset = (query.page - 1) * query.limit

        # execute query
        employees_code = await self.prisma.employees.find_many(
            where=where,
            take=query.limit,
            skip=offset,
            order=order
        )

        total = await self.prisma.employees.count(where=where)

        return employees_code, total
    
    async def update(self, employee_id: str, employee_data: UpdateEmployeeDto) -> Optional[employees]:
        
        update_data = {}

        if employee_data.full_name is not None:
            update_data["full_name"] = employee_data.full_name
        if employee_data.position is not None:
            update_data["position"] = employee_data.position
        if employee_data.department is not None:
            update_data["deoartment"] = employee_data.department
        if employee_data.basic_salary is not None:
            update_data["basic_salary"] = employee_data.basic_salary
        if employee_data.email is not None:
            update_data["email"] = employee_data.email
        if employee_data.phone is not None:
            update_data["phone"] = employee_data.phone
        if employee_data.bank_account is not None:
            update_data["bank_account"] = employee_data.bank_account
        if employee_data.bank_name is not None:
            update_data["bank_name"] = employee_data.bank_name
        if employee_data.status is not None:
            update_data["status"] = employee_data.status
        if employee_data.is_active is not None:
            update_data["is_active"] = employee_data.is_active
        if employee_data.photo_url is not None:
            update_data["photo_url"] = employee_data.photo_url

        # always update timestamp
        update_data["updated_at"] = datetime.now()

        if not update_data:
            return None

        return await self.prisma.employees.update(
            where={"employee_id": employee_id},
            data=update_data
        )
    
    async def soft_delete(self, employee_id: str) -> bool:
        # soft delete implement
        try:
            await self.prisma.update(
                where = {
                    "employee_id": employee_id
                },
                data = {
                    "is_active": False,
                    "status": "INACTIVE",
                    "updated_at": datetime.now()
                }
            )

            return True
        except Exception as e:
            return False
        
    
    async def hard_delete(self, employee_id: str) -> bool:
        #permanent delete implement
        try: 
            await self.prisma.employees.delete(
                where = {
                    "employee_id": employee_id
                }
            )
            return True
        except Exception as e:
            return False
        
    async def get_departments(self) -> List[str]:

        result = await self.prisma.query_raw(
            "SELECT DISTINCT department FROM employees WHERE department IS NOT NULL AND is_active = true ORDER BY department"
        )

        return [row["department"] for row in result if row["department"]]
    
    async def get_employee_count(self) -> dict:

        total = await self.prisma.employees.count()
        active = await self.prisma.employees.count(where={"is_active": True})
        inactive = await self.prisma.employees.count(where={"is_active": False})

        return {
            "total": total,
            "active": active,
            "inactive": inactive
        }