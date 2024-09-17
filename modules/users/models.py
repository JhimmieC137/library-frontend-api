import uuid
import enum
from sqlalchemy import (TIMESTAMP, Column, ForeignKey, 
                        String, Boolean, text, Enum, Integer, 
                        Text, cast, Index, Table)
from sqlalchemy.dialects.postgresql import ARRAY, array
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy_mixins import AllFeaturesMixin

from core.dependencies.sessions import Base


class UserType(str, enum.Enum):
    USER = 'USER'
    ADMIN = 'ADMIN'



class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    first_name = Column(String,  nullable=False)
    last_name = Column(String,  nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(Enum(UserType), server_default = UserType.USER, nullable=False)
    
    user_profile = relationship('UserProfile', uselist=False, back_populates="user", lazy='select')

    # user active checks
    is_active = Column(Boolean, nullable=False, server_default='True')

    # Audit logs
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"), onupdate=text("now()"))
    deactivated_at = Column(TIMESTAMP(timezone=True),
                        nullable=True)
    
    def __repr__(self):
        return f"<User {self.email}>"

    
            


class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4) 
    user =  relationship('User')
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    photo = Column(String, nullable=True)

    # Audit logs
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"), onupdate=text("now()"))
    
    def __repr__(self):
        return f"<Customer Profile: {self.id}>"