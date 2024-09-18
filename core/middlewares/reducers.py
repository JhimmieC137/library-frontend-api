from uuid import UUID
from datetime import datetime
from modules.users.repository import UserRepository
from modules.users.schemas import BaseUser, BaseUserProfile
from modules.users.models import User
from modules.transactions.repository import TransactionRepository, BookRepository
from modules.transactions.schemas import CreateTransaction, CreateBook, UpdateBook, UpdateTransaction, BaseTransaction, BaseBook



userRepo = UserRepository()
transactionRepo = TransactionRepository()
bookRepo = BookRepository()


 
def act_on_users(action: str, payload, id: UUID = None):
    match action:
        case "create_user":
            try:
                userRepo.create(payload=BaseUser(**payload))
            
            except Exception as error:
                raise error
            
        case "update_user":
            try:
                userRepo.partial_update_user_profile(payload=BaseUser(**payload), user_id=id)
            
            except Exception as error:
                raise error
    
 
def act_on_transactions(action: str, payload, id: UUID = None):
    match action:
        case "create_transactions":
            try:
                transactionRepo.create(payload=BaseTransaction(**payload))
            
            except Exception as error:
                raise error
    
 
def act_on_books(action: str, payload, id: UUID = None):
    match action:
        case "create_book":
            try:
                print("create_book")
                bookRepo.create_book(payload=BaseBook(**payload))
            
            except Exception as error:
                raise error
        
        case "update_book":
            try:
                print("update_book")
                bookRepo.update_book(payload=UpdateBook(**payload), book_id=id)
            
            except Exception as error:
                raise error
        
        case "remove_book":
            try:
                print("remove_book")
                bookRepo.delete_book(book_id=id)
            
            except Exception as error:
                raise error
            
    