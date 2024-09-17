from enum import Enum
from typing_extensions  import Annotated
from typing import List
from starlette.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration

from core.router import router
from core.env import config
from core.exceptions import CustomException
from core.dependencies import Logging, engine, Base
from core.middlewares import (
    # AuthenticationMiddleware,
    # AuthBackend,
    # SQLAlchemyMiddleware,
    ResponseLogMiddleware,
)
# from core.helpers.cache import Cache, RedisBackend, CustomKeyMaker
from core.exceptions.handler import http_exception_handler, request_validation_exception_handler, unhandled_exception_handler
from core.middlewares.response_log import log_request_middleware
import pika
# Connect to RabbitMQ
credentials = pika.PlainCredentials(config.RABBIT_MQ_USER, config.RABBITMQ_DEFAULT_PASS)
parameters = pika.ConnectionParameters(config.RABBITMQ_HOSTNAME,
                                       config.RABBITMQ_PORT,
                                       'ashvdjpb',
                                       credentials)
connection = pika.BlockingConnection(parameters=parameters) # add container name in docker
channel = connection.channel()
channel.queue_declare(queue='rpc_queue')


def init_db(app_: FastAPI) -> None:
    Base.metadata.create_all(bind=engine, checkfirst=True)

def init_routers(app_: FastAPI) -> None:
    app_.include_router(router)


def init_listeners(app_: FastAPI) -> None:
    # Exception handler
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "message": exc.message},
        )


def on_auth_error(request: Request, exc: Exception):
    status_code, error_code, message = 401, None, str(exc)
    if isinstance(exc, CustomException):
        status_code = int(exc.code)
        error_code = exc.error_code
        message = exc.message

    return JSONResponse(
        status_code=status_code,
        content={"code": status_code,"error_code": error_code, "message": message},
    )


def init_middleware(app_: FastAPI) -> None:
    app_.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY, same_site='lax')
    app_.add_middleware(
        CORSMiddleware,
        allow_origins=['http://localhost:3000/',
                        'http://localhost:8000/', '*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    # app_.add_middleware(
    #     AuthenticationMiddleware,
    #     backend=AuthBackend(),
    #     on_error=on_auth_error,
    # )
    # Middleware(SQLAlchemyMiddleware),
    app_.add_middleware(ResponseLogMiddleware)
    app_.middleware("http")(log_request_middleware)
    app_.add_middleware(SentryAsgiMiddleware)

def init_exception_handlers(app_: FastAPI) -> None:
    app_.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app_.add_exception_handler(HTTPException, http_exception_handler)
    app_.add_exception_handler(Exception, unhandled_exception_handler)
# def init_cache() -> None:
#     Cache.init(backend=RedisBackend(), key_maker=CustomKeyMaker())


# Sentry bug tracking
sentry_sdk.init(
    dsn=config.SENTRY_DSN,
    traces_sample_rate= 0.5 if config.ENV == "production" else 1.0,
    integrations=[StarletteIntegration(
                        transaction_style="endpoint"
                    ),
                  FastApiIntegration(
                        transaction_style="endpoint"
                    ),
                ],
    enable_tracing=True,
    environment=config.ENV,
)

def create_app() -> FastAPI:
    app_ = FastAPI(
        title="Library Application - Client/Frontend Api",
        description="An assessment by Cowrywise",
        version="1.0.0",
        docs_url=None if config.ENV == "production" else "/docs",
        redoc_url=None if config.ENV == "production" else "/redoc",
        dependencies=[Depends(Logging)],
        # openapi_tags=tags_metadata
    )
    init_db(app_=app_)
    init_routers(app_=app_)
    init_listeners(app_=app_)
    init_middleware(app_=app_)
    init_exception_handlers(app_=app_)
    # init_cache()
    return app_

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

print(" [x] Awaiting RPC requests")
channel.start_consuming()


app = create_app()