from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar("T")

class ResponseBase(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation successful"
    data: Optional[T] = None
    error: Optional[str] = None

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    has_next: bool
