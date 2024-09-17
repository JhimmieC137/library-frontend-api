# import os
# import base64
# from datetime import datetime, timedelta
# from typing import Annotated

# import jwt
# from starlette.config import Config
# from authlib.integrations.starlette_client import OAuth
# from fastapi import Depends, Request, HTTPException
# from fastapi.security import OAuth2PasswordBearer
# from sqlalchemy.orm import Session, joinedload
# from fastapi.encoders import jsonable_encoder

# from modules.users.schemas import *
# from modules.auth.schemas import RefreshTokenSchema
# # from modules.auth.repository import BlacklistRepo
# from modules.auth.models import TokenBlacklist
# from modules.users.models import *

# from core.env import config
# from core.dependencies.sessions import get_db
# from core.exceptions.base import UnauthorizedException, InternalServerErrorException, BadRequestException
# from core.exceptions.auth import DecodeTokenException, ExpiredTokenException, UserNotFoundException


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


# # Set up oauth
# config_data = {'GOOGLE_CLIENT_ID': config.GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': config.GOOGLE_CLIENT_SECRET}
# starlette_config = Config(environ=config_data)
# custom_oauth = OAuth(starlette_config)

# # google reg
# custom_oauth.register(
#     name='google',
#     server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
#     client_kwargs={'scope': 'openid email profile'},
# )
# # linkedin reg
# # custom_oauth.register(name="linkedin",)



# class TokenHelper:
#     @staticmethod
#     def encode(data: dict, expire_period: int = 18000) -> str:
#         token = jwt.encode(
#             payload = {
#                 "id": data["id"],
#                 "role": data["role"],
#                 "is_active": data["is_active"],
#                 "exp": datetime.now() + timedelta(seconds=expire_period),
#             },
#             key=config.JWT_SECRET_KEY
#         )
#         return token

#     @staticmethod
#     def decode(token: str) -> dict:
#         try:
#             return jwt.decode(
#                 token,
#                 config.JWT_SECRET_KEY,
#             )
            
#         except Exception as error:
#             raise error

#     @staticmethod
#     def decode_expired_token(token: str) -> dict:
#         try:
#             return jwt.decode(
#                 token,
#                 config.JWT_SECRET_KEY,
#                 config.JWT_ALGORITHM,
#                 options={"verify_exp": False},
#             )
#         except jwt.exceptions.DecodeError:
#             raise DecodeTokenException("Token has expired")
        
#     async def create_refresh_token(
#         self,
#         token: str,
#         refresh_token: str,
#     ) -> RefreshTokenSchema:
#         token = TokenHelper.decode(token=token)
#         refresh_token = TokenHelper.decode(token=refresh_token)
#         if refresh_token.get("sub") != "refresh":
#             raise DecodeTokenException("Token has expired")

#         return RefreshTokenSchema(
#             token=TokenHelper.encode(payload={"user_id": token.get("user_id")}),
#             refresh_token=TokenHelper.encode(payload={"sub": "refresh"}),
#         )


# async def get_current_user(request: Request, token: Annotated[str, Depends(oauth2_scheme)], 
#                            db: Session = Depends(get_db)) -> BaseUser:
#     user_decoded_string : str
#     # TODO: Refactor token capture, decode and validation into middleware [using oauth bearer doesnt work in middleware]
#     # Get decoded token from auth middleware
    
#     try:
#         if request.user:
#             user_decoded_string = request.user  
#         else: # Get token from headers
#             user_decoded_string = TokenHelper.decode(token)
#     except jwt.exceptions.DecodeError:
#         raise DecodeTokenException("Something went wrong decoding your access token")
#     except jwt.exceptions.ExpiredSignatureError:
#         raise ExpiredTokenException("Token expired, please request for a new verification code")
    

#     blacklisted = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
    
#     if blacklisted:
#         raise ExpiredTokenException("Token invalid or expired")
    

#     user_id: str = user_decoded_string.get("id")

#     if user_id is None:
#         raise DecodeTokenException(message="Invalid token")
    
#     else:
#         user: User = db.query(User).filter(User.id == user_id).first()
        
#         if not user:
#             raise UserNotFoundException
        
#         user_obj: BaseUser = BaseUser.from_orm(user)
#         user_obj.kyc_completed = user.is_kyc_completed()
                
#     return user_obj

# async def get_current_user_and_token(request: Request, token: Annotated[str, Depends(oauth2_scheme)], 
#                            db: Session = Depends(get_db)) -> AuthUser:
#     user_decoded_string : str
#     # TODO: Refactor token capture, decode and validation into middleware [using oauth bearer doesnt work in middleware]
#     # Get decoded token from auth middleware
    
#     try:
#         if request.user:
#             user_decoded_string = request.user  
#         else: # Get token from headers
#             user_decoded_string = TokenHelper.decode(token)
#     except jwt.exceptions.DecodeError:
#         raise DecodeTokenException("Something went wrong decoding your access token")
#     except jwt.exceptions.ExpiredSignatureError:
#         raise ExpiredTokenException("Token expired, please request for a new verification code")
    

#     blacklisted = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
    
#     if blacklisted:
#         raise ExpiredTokenException("Token invalid or expired")
    

#     user_id: str = user_decoded_string.get("id")

#     if user_id is None:
#         raise DecodeTokenException(message="Invalid token")
    
#     else:
#         user: User = db.query(User).filter(User.id == user_id).first()
        
#         if not user:
#             raise UserNotFoundException
        
#         user_obj: BaseUser = BaseUser.from_orm(user)
#         user_obj.kyc_completed = user.is_kyc_completed()
    
#     auth_response: AuthUser = AuthUser(
#         **user_obj.dict(),
#         token = token
#     )
    
#     return auth_response


# async def get_current_user_object(
#     request: Request, 
#     token: Annotated[str, Depends(oauth2_scheme)], 
#     db: Session = Depends(get_db)
# ) -> User:
#     user_decoded_string : str
#     # TODO: Refactor token capture, decode and validation into middleware [using oauth bearer doesnt work in middleware]
#     # Get decoded token from auth middleware
    
#     try:
#         if request.user:
#             user_decoded_string = request.user
        
#         else:
#             user_decoded_string = TokenHelper.decode(token)
            
#     except jwt.exceptions.DecodeError:
#         raise DecodeTokenException("Something went wrong decoding your access token")
    
#     except jwt.exceptions.ExpiredSignatureError:
#         raise ExpiredTokenException("Token expired, please request for a new verification code")
    
    
#     user_id: str = user_decoded_string.get("id")
#     if user_id is None:
#         raise DecodeTokenException(message="Invalid token")


#     user: User = db.query(User).filter(User.id == user_id).first()
#     if user is None:
#         raise UserNotFoundException
    
#     return user



# async def tokenify_user(user: BaseUser) -> AuthUser:
#     try:
#         user_data: AuthUser = { 
#             **user.dict(), 
#             "token": TokenHelper.encode({
#                 "id": str(user.id),
#                 "role": user.role,
#                 "is_active": user.is_active 
#             })
#         }
        
#     except:
#         raise InternalServerErrorException("Something went wrong")
    
#     return user_data