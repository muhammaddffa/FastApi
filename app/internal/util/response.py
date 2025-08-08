from fastapi.responses import JSONResponse
from app.dto.response_dto import ResponseModel, ErrorResponseModel

def success_response(message: str, data: dict, status_code: int = 200):
    return JSONResponse(
        status_code=status_code,
        content=ResponseModel(success=status_code, message=message, data=data).dict()
    )

def error_response(message: str, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponseModel(success=status_code, message=message, data={}).dict()
    )
