from uuid import UUID
from datetime import datetime
from typing import Annotated, Any, List, Optional
from pydantic import field_validator, ConfigDict, BaseModel, Field, EmailStr, constr, HttpUrl


from modules.users.models import UserType # Wildcard "*" cannot be used for some
from .models import TransactionStatus, BookCategory, BookStatus


####################### Users ################# 

class BaseTransaction(BaseModel):
    id: Optional[UUID] = None
    book_id: Optional[UUID] = None
    book_name: Optional[str] = None
    user_id: Optional[UUID] = None
    user_email: EmailStr = Field(None, description="email")
    status : Optional[TransactionStatus] = None
    created_at: Optional[datetime] = None
    return_date: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

class CreateTransaction(BaseModel):
    book_id: Optional[UUID] = None
    book_name: Optional[str] = None
    user_id: Optional[UUID] = None
    user_email: EmailStr = Field(None, description="email")
    user_id: UUID = None
    status: Optional[TransactionStatus] = None
    days_till_return: Optional[int] = None
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

class UpdateTransaction(BaseModel):
    id: Optional[UUID] = None
    book_id: Optional[UUID] = None
    book_name: Optional[str] = None
    user_id: Optional[UUID] = None
    user_email: EmailStr = Field(None, description="email")
    user_id: UUID = None
    status : Optional[TransactionStatus] = None
    days_till_return: Optional[int] = None
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)


class BaseBook(BaseModel):
    id: Optional[UUID] = None
    name: Optional[str] = None
    author: Optional[str] = None
    publishers: Optional[str] = None
    category: Optional[BookCategory] = None
    status: Optional[BookStatus] = None
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)