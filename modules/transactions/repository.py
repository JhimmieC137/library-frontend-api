from datetime import datetime, timedelta
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

from modules.users.models import User
from .models import Transaction, Book, TransactionStatus, BookCategory, BookStatus
from .schemas import *

class TransactionRepository:
    def __init__(self) -> None:
        self.db: Session = get_db().__next__()

    async def create(self, payload: CreateTransaction) -> BaseTransaction:
        user = self.db.query(User).filter(User.id == payload.user_id).first()
        if user is None:
            raise NotFoundException("User not found!")
               
        try:
            new_transaction = Transaction(**payload.dict())
            new_transaction.return_date = datetime.now() + timedelta(payload.days_till_return)

            self.db.add(new_transaction)
            self.db.commit()
            self.db.refresh(new_transaction)
        
        except:
            raise InternalServerErrorException("Something went wrong creating the transaction")
            
        
        
        book: Book = self.db.query(Book).filter(Book.id == payload.book_id).first()
    
        if book is None:
            raise NotFoundException("Book not found!")
        
        try:
            book.status = BookStatus.BORROWED if payload.status == TransactionStatus.BORROWING else BookStatus.AVAILABLE
            self.db.commit()
            
        except:
            raise InternalServerErrorException("Something went wrong updating book's status")
        
        return new_transaction


    async def get_transaction_list(self, page: int, limit: int, user_id: UUID, status: TransactionStatus = None) -> tuple[List[Transaction], int]:
        skip = (page - 1) * limit
        transaction_query = self.db.query(Transaction).filter(
                                                            Transaction.user_id == user_id
                                                        )
        if status:
            transaction_query = transaction_query.filter(
                Transaction.status == status
            )
                    
        
        transaction_count: int = transaction_query.count()
        transactions: List[Transaction] = transaction_query.order_by(Transaction.created_at.desc()).limit(limit).offset(skip).all()
        
        return transactions, transaction_count
    
    
    async def get_transaction_by_id(self, transaction_id: UUID) -> Transaction:
        transaction: Transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
        if transaction is None:
            raise NotFoundException("Transaction not found!")
        
        return Transaction
        
    # async def update_tansaction(self, payload: UpdateTransaction, transaction_id: UUID):
    #     # Check for transaction
    #     transaction_query = self.db.query(Transaction).filter(Transaction.id == transaction_id)
    #     transaction: Transaction = transaction_query.first() 
    #     if transaction is None:
    #         raise NotFoundException("Transaction not found!")
        
    #     # Check for user
    #     user = self.db.query(User).filter(User.id == payload.user_id).first()
    #     if user is None:
    #         raise NotFoundException("User not found!")
        
    #     # Check for book
    #     book: Book = self.db.query(Book).filter(Book.id == payload.book_id).first()
    #     if book is None:
    #         raise NotFoundException("Book not found!")
             
    #     # Transaction update
    #     try:
    #         transaction_query.update(payload.dict(exclude_unset = True))
    #         if payload.days_till_return:
    #             transaction.return_date += timedelta(payload.days_till_return)
    #         
    #         self.db.commit()
            
    #     except:
    #         raise InternalServerErrorException("Something went wrong updating transaction")
        
        
class BookRepository:
    async def get_book_list(self, page: int, limit: int, search: str, publishers: str = None, category: BookCategory = None, status: BookStatus = None) -> tuple[List[Book], int]:
        skip = (page - 1) * limit
        book_query = self.db.query(Book)\
                    .filter(or_(
                        Book.name.ilike(f"%{search}%"), 
                        # Book.publishers.ilike(f"%{search}%"),
                    ))
        
        if publishers:
            book_query = book_query.filter(or_(
                Book.publishers.ilike(f"%{search}%"),
            ))
        
        if category:
            book_query = book_query.filter(
                Book.category == category
            )
        
        if status:
            book_query = book_query.filter(
                Book.status == status
            )
                    
        
        book_count: int = book_query.count()
        books: List[Book] = book_query.order_by(Book.created_at.desc()).limit(limit).offset(skip).all()
        
        return books, book_count
    
    
    async def get_book_by_id(self, book_id: UUID) -> Book:
        book: Book = self.db.query(Book).filter(Book.id == book_id).first()
    
        if book is None:
            raise NotFoundException("Book not found!")
        
        return book