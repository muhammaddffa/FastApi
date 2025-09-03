from pydantic import BaseModel
from typing import Any, Optional, Generic, TypeVar

T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: Optional[T] = None

class ErrorResponseModel(BaseModel):
    success: bool = False
    message: str
    error: Optional[str] = None

class ResponseDTO(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None    
    error: Optional[str] = None

class PaginationDTO(BaseModel):
    page: int
    size: int
    total: int
    total_pages: int

class PaginatedResponseDTO(ResponseDTO[T]):
    pagination: Optional[PaginationDTO] = None