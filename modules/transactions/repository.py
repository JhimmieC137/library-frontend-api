from datetime import datetime, timedelta
from uuid import UUID, uuid4
from typing import List, Union
from slugify import slugify

from sqlalchemy.orm import Session
from sqlalchemy import or_


from core.dependencies.sessions import get_db
from core.helpers.mail_utils import *
from core.exceptions.base import DuplicateValueException, UnprocessableEntity, BadRequestException, InternalServerErrorException
from core.exceptions import NotFoundException

from modules.users.models import User
from .models import Transaction, Book, TransactionStatus, BookCategory, BookStatus
from .schemas import *

class TransactionRepository:
    def __init__(self) -> None:
        self.db: Session = get_db().__next__()
        

    def create(self, payload: Union[CreateTransaction, BaseTransaction]) -> BaseTransaction: # type: ignore
        user: User = self.db.query(User).filter(User.id == payload.user_id).first()
        if user is None:
            raise NotFoundException("User not found!")
            
        book: Book = self.db.query(Book).filter(Book.id == payload.book_id).first()
        
        if book is None:
            raise NotFoundException("Book not found!")
        elif book and book.is_deleted:
            raise BadRequestException("Book no longer available at this library!")
        elif book and book.status == BookStatus.BORROWED and payload.status == TransactionStatus.BORROWING :
            raise UnprocessableEntity("Book has been lent to another user")
        elif book and book.status == BookStatus.BORROWED and payload.status == TransactionStatus.BORROWING :
            raise UnprocessableEntity("Book has been lent to another user")
        elif book and book.status == BookStatus.AVAILABLE and payload.status == TransactionStatus.RETURNING :
            raise UnprocessableEntity("Book has been returned already")
            
        try:
            payload_dict = payload.dict()
            days_till_return = payload_dict.pop('days_till_return')
            
            new_transaction = Transaction(id=uuid4() if type(payload) == CreateTransaction else payload_dict['id'], **payload_dict)
        
            if payload_dict['status'] == TransactionStatus.BORROWING:
                new_transaction.return_date = datetime.now() + timedelta(days_till_return)
                book.status = BookStatus.BORROWED 
                book.holder_id = user.id
                book.holder_email = user.email
            
            else:
                book.status = BookStatus.AVAILABLE 
                book.holder_id = None
                book.holder_email = None
                book.updated_at = datetime.now() if type(payload) == CreateTransaction else payload_dict['created_at']
                
 
            self.db.add(new_transaction)
            self.db.commit()
            self.db.refresh(new_transaction)
            
            return new_transaction
            
        
        except Exception as e:
            print(e)
            self.db.rollback()
            raise InternalServerErrorException("Something went wrong creating the transaction")
        


    def get_transaction_list(self, page: int, limit: int, user_id: UUID = None, status: TransactionStatus = None) -> tuple[List[Transaction], int]:
        skip = (page - 1) * limit
        transaction_query = self.db.query(Transaction)
        
        if status:
            transaction_query = transaction_query.filter(
                Transaction.status == status
            )
        
        if user_id:
            transaction_query = transaction_query.filter(
                Transaction.user_id == user_id
            )
                
        
        transaction_count: int = transaction_query.count()
        transactions: List[Transaction] = transaction_query.order_by(Transaction.created_at.desc()).limit(limit).offset(skip).all()
        
        return transactions, transaction_count
    
    
    def get_transaction_by_id(self, transaction_id: UUID) -> Transaction:
        transaction: Transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
        if transaction is None:
            raise NotFoundException("Transaction not found!")
        
        return Transaction
        
class BookRepository:
    def __init__(self) -> None:
        self.db: Session = get_db().__next__()
        
    def get_book_list(self, page: int, limit: int, search: str, publishers: str = None, category: BookCategory = None, status: BookStatus = None, user_id: UUID = None) -> tuple[List[Book], int]:
        skip = (page - 1) * limit
        
        try:
            book_query = self.db.query(Book).filter(Book.is_deleted == False)\
                        .filter(or_(
                            Book.name.ilike(f"%{search}%"),
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
                
            if user_id:
                book_query = book_query.filter(
                    Book.holder_id == user_id
                )
        
        except:
            raise InternalServerErrorException("Something went wrong fetching the books")
                        
        
        book_count: int = book_query.count()
        books: List[Book] = book_query.order_by(Book.created_at.desc()).limit(limit).offset(skip).all()
        
        return books, book_count
    
    
    def get_book_by_id(self, book_id: UUID) -> Book:
        book: Book = self.db.query(Book).filter(Book.id == book_id).first()
    
        if book is None:
            raise NotFoundException("Book not found!")
        elif book and book.is_deleted:
            raise BadRequestException("Book no longer available at this library!")
            
        
        return book
    
    
    def create_book(self, payload: CreateBook) -> Book:
        book: Book = self.db.query(Book).filter(Book.name == payload.name).first()
        
        if book:
            raise DuplicateValueException("Book already exists!")
        
        new_book = Book(id=uuid4(), **payload.dict())
        
        self.db.add(new_book)
        self.db.commit()
        self.db.refresh(new_book)
        
        return new_book
    
    
    def delete_book(self, book_id: UUID) -> Book:
        book: Book = self.db.query(Book).filter(Book.id == book_id).first()
        
        if book is None:
            raise DuplicateValueException("Book not found!")
        elif book and book.is_deleted:
            raise BadRequestException("Book is already deleted!")
        
        try:
            book.is_deleted = True
            book.deleted_at = datetime.now()
            self.db.commit()
            
        except:
            self.db.rolback()
            raise InternalServerErrorException("Something went wrong removing book from library")
    
    
    def update_book(self, book_id: UUID, payload: UpdateBook) -> Book:
        book_query = self.db.query(Book).filter(Book.id == book_id)
        
        book: Book = book_query.first()
        if book is None:
            raise DuplicateValueException("Book not found!")
        elif book and book.is_deleted:
            raise BadRequestException("Book is already deleted!")
        
        try:
            book_query.update(payload.dict(exclude_unset=True))
            self.db.commit()
            
            return book
            
        except:
            self.db.rolback()
            raise InternalServerErrorException("Something went wrong updating book")
            