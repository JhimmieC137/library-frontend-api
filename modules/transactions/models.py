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

class TransactionStatus(str, enum.Enum):
    BORROWING = 'BORROWING'
    RETURNING = 'RETURNING'

class BookStatus(str, enum.Enum):
    BORROWED = 'BORROWED'
    AVAILABLE = 'AVAILABLE'

class BookCategory(str, enum.Enum):
    FICTION = 'FICTION'
    SCIENCE_FICTION = 'SCIENCE_FICTION'
    TECHNOLOGY = 'TECHNOLOGY'
    SCIENCE = 'SCIENCE'
    HORROR = 'HORROR'
    ROMANCE = 'ROMANCE'
    ACTION = 'ACTION'




class Book(Base):
    __tablename__ = "books"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    name = Column(String,  nullable=False)
    author = Column(String,  nullable=False)
    publishers = Column(String,  nullable=False)
    category = Column(Enum(BookCategory), server_default = BookCategory.ACTION, nullable=False)
    status = Column(Enum(BookStatus), server_default = BookStatus.BORROWED, nullable=False)
        
    # Audit logs
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"), onupdate=text("now()"))
    
    def __repr__(self):
        return f"<User {self.id}>"


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    
    # Book info
    book_id = Column(UUID(as_uuid=True), nullable=False)
    book_name = Column(String, nullable=False, server_default = "Anonymous by John Doe")
    
    # User info
    user_id = Column(UUID(as_uuid=True), nullable=False)
    user_email = Column(String, nullable=False, server_default = "example@mail.com")
    
    status = Column(Enum(TransactionStatus), server_default = TransactionStatus.BORROWING, nullable=False)
    
    return_date = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Audit logs
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"), onupdate=text("now()"))
    
    def __repr__(self):
        return f"<User {self.id}>"