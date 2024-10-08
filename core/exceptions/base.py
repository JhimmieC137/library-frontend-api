from http import HTTPStatus
from fastapi import HTTPException

class CustomException(Exception):
    code = HTTPStatus.BAD_GATEWAY
    status_code = code
    error_code = HTTPStatus.BAD_GATEWAY
    message = HTTPStatus.BAD_GATEWAY.description
    detail = message

    def __init__(self, message=None, ):
        if message:
            self.message = message


class BadRequestException(CustomException):
    code = HTTPStatus.BAD_REQUEST
    error_code = HTTPStatus.BAD_REQUEST
    message = HTTPStatus.BAD_REQUEST.description


class NotFoundException(CustomException):
    code = HTTPStatus.NOT_FOUND
    error_code = HTTPStatus.NOT_FOUND
    message = HTTPStatus.NOT_FOUND.description


class ForbiddenException(CustomException):
    code = HTTPStatus.FORBIDDEN
    error_code = HTTPStatus.FORBIDDEN
    message = HTTPStatus.FORBIDDEN.description


class UnauthorizedException(CustomException):
    code = HTTPStatus.UNAUTHORIZED
    error_code = HTTPStatus.UNAUTHORIZED
    message = HTTPStatus.UNAUTHORIZED.description


class UnprocessableEntity(CustomException):
    code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = HTTPStatus.UNPROCESSABLE_ENTITY
    message = HTTPStatus.UNPROCESSABLE_ENTITY.description


class DuplicateValueException(CustomException):
    code = HTTPStatus.CONFLICT
    error_code = HTTPStatus.CONFLICT
    message = HTTPStatus.CONFLICT.description


class InternalServerErrorException(CustomException):
    code = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code = HTTPStatus.INTERNAL_SERVER_ERROR
    message = HTTPStatus.INTERNAL_SERVER_ERROR.description
