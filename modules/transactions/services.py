from typing import Annotated, Optional
from core.helpers.mail_utils import *
from uuid import UUID

from fastapi import Depends, status, APIRouter, Path
from sqlalchemy.orm import Session

from core.env import config
from core.dependencies.sessions import get_db
# from core.dependencies.auth import get_current_user
from core.exceptions import *
from core.helpers.schemas import CustomListResponse, CustomResponse

from .models import *
from .schemas import *
from .repository import TransactionRepository, BookRepository
import pika
import json


# Connect to RabbitMQ
credentials = pika.PlainCredentials(config.RABBIT_MQ_USER, config.RABBITMQ_DEFAULT_PASS)
parameters = pika.ConnectionParameters(config.RABBITMQ_HOSTNAME,
                                       config.RABBITMQ_PORT,
                                       'ashvdjpb',
                                       credentials)
connection = pika.BlockingConnection(parameters=parameters) # add container name in docker
channel = connection.channel()
channel.queue_declare(queue='rpc_queue')


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


def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)

def on_request(ch, method, props, body):
    n = int(body)

    print(f" [.] fib({n}) nice")
    response = fib(n)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

print(" [x] Awaiting RPC requestsss")
channel.start_consuming()