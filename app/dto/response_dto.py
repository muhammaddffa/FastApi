from pydantic import BaseModel
from typing import Any, Optional, Generic, TypeVar

T = TypeVar('T')

class ResponseDto(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    error: Optional[str] = None

class PaginationDTO(BaseModel):
    page: int
    size: int
    total: int
    total_pages: int

class PaginationReponseDto(BaseModel):
    # success: bool
    # message: str
    # data: list[Any]
    pagination: Optional[PaginationDTO] = None
    