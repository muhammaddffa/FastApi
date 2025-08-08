from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")

class ResponseModel(BaseModel, Generic[T]):
    success: int
    message: str
    data: Optional[T]

class ErrorResponseModel(BaseModel):
    success: int
    message: str
    data: dict={}