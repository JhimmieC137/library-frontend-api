from uuid import UUID
from datetime import datetime
from typing import Annotated, Any, List, Optional
from pydantic import ConfigDict, BaseModel, Field, EmailStr, constr, HttpUrl


from modules.users.models import UserType # Wildcard "*" cannot be used for some



####################### Users ################# 

class BaseUserProfile(BaseModel):
    id: Optional[UUID] = None
    user_id: UUID = None
    address: Optional[str] = None
    phone: Optional[str] = None
    photo: Optional[str] = None
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

class BaseUser(BaseModel):
    id: Optional[UUID] = None
    email: EmailStr = Field(None, description="email")
    first_name: str = Field(None, description="First Name")
    last_name: str = Field(None, description="Last Name")
    role: Optional[UserType] = None
    is_active: Optional[bool] = None
    user_profile : Optional[BaseUserProfile] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)


class UpdateUserProfile(BaseModel):
    first_name: str = Field(None, description="First Name")
    last_name: str = Field(None, description="Last Name")
    email: EmailStr = Field(None, description="Email")
    photo: Optional[str] = None
    user_profile : Optional[BaseUserProfile] = None
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

class FetchUserSchema(BaseModel):
    email: EmailStr
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

class CreateUserSchema(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

class FindUserSchema(BaseModel):
    email: EmailStr
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)
    