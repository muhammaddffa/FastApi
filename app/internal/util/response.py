from typing import Any, Optional
from app.dto.response_dto import ResponseDTO

def success_response(message: str, data: Any = None) -> ResponseDTO:
    return ResponseDTO(
        success=True,
        message=message,
        data=data,
        error=None
    )

def error_response(message: str, error: str = None) -> ResponseDTO:
    return ResponseDTO(
        success=False,
        message=message,
        data=None,
        error=error or message
    )