from typing import Any, Optional
from app.dto.response_dto import ResponseDTO

def success_response(message: str, data: Any = None) -> dict:
    return ResponseDTO(
        success=True,
        message=message,
        data=data,
        error=None
    ).model_dump()

def error_response(message: str, error: str = None) -> dict:
    return ResponseDTO(
        success=False,
        message=message,
        data=None,
        error=error or message
    ).model_dump()