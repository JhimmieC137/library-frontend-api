from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, ValidationError

DataT = TypeVar('DataT')


# Response Schemas
class CustomResponse(BaseModel, Generic[DataT]):
    status: Optional[str] = 'success'
    code: Optional[int] = 200
    message: Optional[str] = None
    data: Optional[DataT] = None

class CustomListResponse(BaseModel, Generic[DataT]):
    status: Optional[str] = 'success'
    code: Optional[int] = 200
    message: Optional[str] = None
    count: Optional[int] = None
    total_count: Optional[int] =None
    next_page: Optional[int] = None
    data: Optional[List[DataT]] = None
     
