from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Union

from sqlalchemy.orm import Session
from sqlalchemy import or_

from core.dependencies.sessions import get_db
from core.helpers.mail_utils import *
from core.exceptions.auth import DuplicateEmailException
from core.exceptions.base import InternalServerErrorException
from core.exceptions import NotFoundException

from .models import *
from .schemas import *

class UserRepository:
    def __init__(self) -> None:
        self.db: Session = get_db().__next__()

    def create(self, payload: Union[CreateUserSchema, BaseUser]) -> BaseUser:
        user = self.db.query(User).filter(User.email == payload.email.lower()).first()
        
        if user:
            raise DuplicateEmailException("Email taken")
        
        payload.email = payload.email.lower()        
        try:
            if type(payload) == CreateUserSchema:
                new_user = User(id=uuid.uuid4(), **payload.dict())

                self.db.add(new_user)
                self.db.commit()
                self.db.refresh(new_user)
                
                # Create user profile
                new_user_profile = UserProfile(id=uuid.uuid4(), user_id=new_user.id)
                new_user_profile.updated_at = datetime.now()
                self.db.add(new_user_profile)
                
            else:
                new_user = User(id=UUID(payload.id), **payload.dict())
                new_user_profile = UserProfile(id=UUID(payload.user_profile.id), **payload.user_profile.dict())
                
            self.db.commit()
            # new_user.id = str(new_user.id)
            # new_user.user_profile.id = str(new_user.user_profile.id)
            # new_user.user_profile.user_id = str(new_user.user_profile.user_id)
            user_obj: BaseUser = BaseUser.from_orm(new_user)
            
            return user_obj
    
        except Exception as e:
            print(e)
            self.db.rollback()
            raise InternalServerErrorException("Something went wrong creating user")
    
    
    def get_user_by_id(self, user_id: UUID) -> User:
        user: User = self.db.query(User).filter(User.id == user_id).first()
    
        if user is None:
            raise NotFoundException("User not found!")
        
        return user
    
    
    # async def deactivate_user_by_id(self, user_id: UUID) -> User:
    #     user: User = self.db.query(User).filter(User.id == user_id).first()
    
    #     if user is None:
    #         raise NotFoundException("User not found!")
        
    #     return user
    
    
    def get_user_by_email(self, email: str) -> User:
        user = self.db.query(User).filter(User.email == email.lower()).first()
        return user
    
    
    def user_email_update(self, user_id: UUID, new_email: str):
        user: User = self.get_user_by_id(user_id=user_id)
        
        try:
            user.email = new_email
            self.db.commit()
    
        except:
            raise InternalServerErrorException("Something went wrong updating user's email")

        
    def partial_update_user_profile(self, payload: UpdateUserProfile, user_id: UUID):
        user_query = self.db.query(User).filter(User.id == user_id)
        
        user: User = user_query.first()
        if user is None:
            raise NotFoundException("User not found!")
                
        # Profile update
        try:
            user_profile_query = self.db.query(UserProfile).filter(UserProfile.user_id == user.id)
            user_profile = user_profile_query.first()
            
            if user_profile is None and payload.user_profile == None:
                new_profile = UserProfile(user_id = user.id, updated_at = datetime.now())
                self.db.add(new_profile)
            
            elif user_profile is None and payload.user_profile != None:
                new_profile = UserProfile(**payload.user_profile.dict())
                new_profile.user_id = user.id
                new_profile.updated_at = datetime.now()
                self.db.add(new_profile)
            
            elif user_profile is not None and payload.user_profile != None:
                user_profile_query.update(payload.user_profile.dict(exclude_unset=True))
        
        except:
            raise InternalServerErrorException("Something went wrong updating user's profile")
        
        # User Update
        try:
            if payload.first_name:
                user.first_name = payload.first_name
            
            if payload.last_name:
                user.last_name=payload.last_name
        
        except:
            raise InternalServerErrorException("Something went wrong updating user")
                
        # Save
        try:
            self.db.commit()
            self.db.refresh(user)
            
        except:
            raise InternalServerErrorException("Something went wrong saving changes")
        
        return user
        
        
    def get_user_list(self, page: int, limit: int, search: str) -> tuple[List[User], int]:
        skip = (page - 1) * limit
        user_query = self.db.query(User)\
                    .filter(or_(
                        User.first_name.ilike(f"%{search}%"),
                        User.last_name.ilike(f"%{search}%"),
                        User.email.ilike(f"%{search}%"),
                    )).filter(User.is_active == True)
        
        user_count: int = user_query.count()
        user: List[User] = user_query.order_by(User.created_at.desc()).limit(limit).offset(skip).all()
        
        return user, user_count
        