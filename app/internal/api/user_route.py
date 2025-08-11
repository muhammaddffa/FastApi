from fastapi import APIRouter
from app.dto.user_dto import UserCreate
from app.internal.service import user_service
from app.internal.util.response import success_response, error_response

router = APIRouter(prefix="/api", tags=["Users"])

@router.post("/users")
async def create_user(data: UserCreate):
    try:
        result = await user_service.create_user_service(data)
        return success_response("user created successfully", result, status_code=201)
    except Exception as e:
        return error_response(str(e), status_code=400)

@router.get("/users")
async def get_all_users():
    result = await user_service.get_all_users_service()
    return success_response("user list", result)

@router.patch("/users/{id}")
async def update_user(id: str, data: UserCreate):
    try:
        result = await user_service.update_user_service(id, data)
        return success_response("user updated successfully", result)
    except Exception as e:
        return error_response(str(e), status_code=400)

@router.get("/users/{id}")
async def get_user_by_id(id : str):
    try:
        result = await user_service.get_user_by_id_service(id)
        return success_response("user found successfully", result)
    except Exception as e:
        return error_response(str(e), status_code=400)
    
@router.delete("/users/{id}")
async def delete_user(id: str):
    try:
        result = await user_service.delete_user_service(id)
        return success_response("user deleted successfully", result)
    except Exception as e:
        return error_response(str(e), status_code=400)