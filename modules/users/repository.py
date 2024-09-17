from datetime import datetime
from uuid import UUID
from typing import List
from slugify import slugify

from sqlalchemy.orm import Session
from sqlalchemy import or_


from core.dependencies.sessions import get_db
from core.helpers import password
from core.helpers.mail_utils import *
from core.exceptions.auth import DuplicateEmailException
from core.exceptions.base import ForbiddenException, InternalServerErrorException
from core.exceptions import NotFoundException

from .models import *
from .schemas import *

class UserRepository:
    def __init__(self) -> None:
        self.db: Session = get_db().__next__()

    async def create(self, payload: CreateUserSchema) -> BaseUser:
        user = self.db.query(User).filter(User.email == payload.email.lower()).first()
        
        if user:
            raise DuplicateEmailException("Email taken")
        
        # Hash the password
        payload.email = payload.email.lower()
        new_user = User(**payload.dict())

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        
        # Create user profile
        new_user_profile = UserProfile(user_id=new_user.id)
        new_user_profile.updated_at = datetime.now()
        self.db.add(new_user_profile)
            
        self.db.commit()
        user_obj: BaseUser = BaseUser.from_orm(new_user)
        
        return user_obj
    
    async def get_user_by_id(self, user_id: UUID) -> User:
        user: User = self.db.query(User).filter(User.id == user_id).first()
    
        if user is None:
            raise NotFoundException("User not found!")
        
        return user
    
    
    async def get_user_by_email(self, email: str) -> User:
        user = self.db.query(User).filter(User.email == email.lower()).first()
        return user
    
    
    async def user_email_update(self, user_id: UUID, new_email: str):
        user: User = self.get_user_by_id(user_id=user_id)
        
        try:
            user.email = new_email
            self.db.commit()
    
        except:
            raise InternalServerErrorException("Something went wrong updating user's email")

        
    async def partial_update_user_profile(self, payload: UpdateUserProfile, user_id: UUID):
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
        
        except Exception as e:
            print(e)
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
        
        