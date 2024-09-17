from typing import Annotated, Optional
from core.helpers.mail_utils import *
from uuid import UUID

from fastapi import Depends, status, APIRouter, Path
from sqlalchemy.orm import Session

from core.dependencies.sessions import get_db
# from core.dependencies.auth import get_current_user
from core.exceptions import *
from core.helpers.schemas import CustomListResponse, CustomResponse

from .models import UserType
from .schemas import *
from .repository import UserRepository

router = APIRouter(
    prefix="/users", tags=["Users"]
)


userRepo = UserRepository()


# ##################################
# Users
# ##################################

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=CustomResponse[BaseUser], )
async def create_user(
    payload: CreateUserSchema,
) ->  CustomResponse[BaseUser]:
    """
    Enroll users
    """
    try:        
        new_user = await userRepo.create(payload=payload)
        
        return {"message": "User created successfully", "data": new_user, "code": 201}
    
    except Exception as error:
        raise error


@router.post("/details", response_model=CustomResponse[BaseUser])
async def request_user_details(
    payload: FetchUserSchema,
) -> CustomResponse[BaseUser]:
    """
    Fetch user's details/profile 
    """
    try:
        user = await userRepo.get_user_by_email(email=payload.email)

        return {'message': 'User details retrieved successfully', 'data': user}

    except Exception as error:
        raise error


@router.patch('/{user_id}', response_model=CustomResponse[BaseUser])
async def update_user(
    user_id: Annotated[UUID, Path(title="The ID of the User")], 
    payload: Optional[UpdateUserProfile],
) -> CustomResponse[BaseUser]:
    """
    Update user 
    """
    try:        
        user = await userRepo.partial_update_user_profile(payload=payload, user_id=user_id)
        
        return {"message":"User profile updated successfully","data": user}
    
    except Exception as error:
        raise error