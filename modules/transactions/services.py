import json
from typing import Annotated
from core.helpers.mail_utils import *
from uuid import UUID

from fastapi import status, APIRouter, Path
from core.exceptions import *
from core.helpers.schemas import CustomListResponse, CustomResponse
from core.middlewares.messanger import client

from .models import *
from .schemas import *
from .repository import TransactionRepository, BookRepository

router = APIRouter(
    prefix=""
)


transactionRepo = TransactionRepository()
bookRepo = BookRepository()


# ##################################
# Transactions
# ##################################


@router.post('/transactions', status_code=status.HTTP_201_CREATED, response_model=CustomResponse[BaseTransaction], tags=["Transactions"])
async def create_transaction(
    payload: CreateTransaction,
) ->  CustomResponse[BaseTransaction]:
    """
    Create transaction to borrow or Return book
    """
    try:        
        new_transaction = await transactionRepo.create(payload=payload)
        client.send_message(json.dumps({
            "service": "transactions",
            "action": "create_transaction",
            "payload": payload.dict(),
        }))
        return {"message": "Transaction created successfully", "data": new_transaction, "code": 201}
    
    except Exception as error:
        raise error


@router.get('/transactions', response_model=CustomListResponse[BaseTransaction], tags=["Transactions"])
async def fetch_transactions(
    user_id: Annotated[UUID, Path(title="The ID of the User")] = None, 
    limit: int = 10, page: int = 1, 
    status: TransactionStatus = None
) -> CustomListResponse[BaseTransaction]:
    """
    Fetch current user's transactions
    """
    try:
        transactions, transaction_count = await transactionRepo.get_transaction_list(page=page, limit=limit, user_id=user_id, status=status)
        
        return {'message': 'Transaction list fetched successfully', 'total_count': transaction_count, 'count': len(transactions), 'next_page': page + 1,'data': transactions}
    
    except Exception as error:
        raise error
    

@router.get('/transactions/{transaction_id}', response_model=CustomResponse[BaseTransaction], tags=["Transactions"])
async def retrieve_transaction(
    transaction_id: Annotated[UUID, Path(title="The ID of the Transaction")], 
) -> CustomResponse[BaseTransaction]:
    """
    Fetch current user's transactions
    """
    try:
        transaction = transactionRepo.get_transaction_by_id(transaction_id=transaction_id)
        
        return {"message": "Transaction retrieved successfully", "data": transaction}
    
    except Exception as error:
        raise error





# ##################################
# Books
# ##################################

# async def register_new_book(
#     payload: CreateBook,
# ) -> CustomResponse[BaseBook]:
#     try:
#         new_book = await bookRepo.create_book(payload=payload)

#         return  {"message": "Book created successfully", "data": new_book}
    
#     except Exception as error:
#         raise error
    

@router.get('/books', response_model=CustomListResponse[BaseBook], tags=["Books"])
async def fetch_books(
    current_holder_id: Annotated[UUID, Path(title="The ID of the User")] = None,
    limit: int = 10, page: int = 1, search: str = '',
    publishers: str = None,
    status: BookStatus = BookStatus.AVAILABLE,
    category: BookCategory = None,
) -> CustomListResponse[BaseBook]:
    """
    Fetch list of books
    """
    try:
        
        books, book_count = await bookRepo.get_book_list(
                                                        page=page, 
                                                        limit=limit, 
                                                        search=search, 
                                                        status=status, 
                                                        category=category, 
                                                        publishers=publishers,
                                                        user_id=current_holder_id
                                                    )
        print("Here")
        client.send_message(json.dumps({"message": "Gume", "number": 5637}))
        return {'message': 'Book list fetched successfully', 'total_count': book_count, 'count': len(books), 'next_page': page + 1,'data': books}
    
    except Exception as error:
        raise error
    

@router.get('/books/{book_id}', response_model=CustomResponse[BaseBook], tags=["Books"])
async def retrieve_book(
    book_id: Annotated[UUID, Path(title="The ID of the Book")], 
) -> CustomResponse[BaseBook]:
    """
    Retrieve book
    """
    try:
        book = await bookRepo.get_book_by_id(book_id=book_id)
        
        return {"message": "Book retrieved successfully", "data": book}
    
    except Exception as error:
        raise error


# async def remove_book(
#     book_id: Annotated[UUID, Path(title="The ID of the Book")], 
# ):
#     try:
#         await bookRepo.delete_book(book_id=book_id)
    
#     except Exception as error:
#         raise error