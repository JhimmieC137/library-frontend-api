# from typing import Union

# from fastapi.encoders import jsonable_encoder

# from core.exceptions.base import *
# # from core.dependencies.auth import TokenHelper
# from core.dependencies.mail import EmailSender
# from core.helpers.schemas import EmailParameters, CandidateWelcomeEmail, ClientWelcomeEmail, PasswordResetEmail, EmailTokenExp, VerificationEmail, InvitationEmail
# from core.env import config


# from modules.users.schemas import *
# from modules.users.models import User


# CLIENT_WELCOME_MAIL = 32987230
# CANDIDATE_WELCOME_MAIL = 33384666
# PASSWORD_RESET_MAIL = 32990683
# EMAIL_VERIFICATION = 33975638
# CLIENT_INVITATION = 34056042


# def mail_notify(mail_to: str, template: int, req_parameters: Union[CandidateWelcomeEmail, ClientWelcomeEmail, PasswordResetEmail]) -> None:
    
#     EmailSender.send_mail( EmailParameters(
#         recipient_mail= mail_to,
#         template_id= template,
#         template_values= req_parameters.dict())
#     )


# def send_welcome_mail(email: str, first_name: str, template: int):
#     try:
#         welcome_mail_payload = ClientWelcomeEmail(first_name = first_name)
#         print(welcome_mail_payload)
#         print(welcome_mail_payload.dict())
#         # mail_notify(email, template, welcome_mail_payload)

#     except:
#         raise InternalServerErrorException("Something went wrong sending welcome mail")

# def send_password_reset_mail(user: User):
#     try:
#         data = {"token": TokenHelper.encode(
#             jsonable_encoder({"id": user.id})
#         )}
#         email_payload = PasswordResetEmail(first_name = user.first_name, action_url = f'{config.CLIENT_CANDIDATE_BASE_URL}{config.AUTH}{config.CHANGE_PASSWORD}/{data["token"].decode()}')
#         print(email_payload)
#         print(email_payload.dict())
#         # mail_notify(user.email, PASSWORD_RESET_MAIL, email_payload)
    
#     except Exception as e:
#         print(e)
#         raise InternalServerErrorException("Something went wrong sending password reset mail")


# def send_verification_mail(user: User, expiriy: dict = EmailTokenExp().__dict__):
#     try:
#         auth_data = {"token": TokenHelper.encode(
#             jsonable_encoder({"id": user.id}),
#             expiriy['seconds']
#         )}
#         # auth_data = {"token":TokenHelper.encode(jsonable_encoder(BaseUser.from_orm(user)), expiriy['seconds'])}
#         email_payload = VerificationEmail(first_name = user.first_name, action_url = f'{config.CLIENT_CANDIDATE_BASE_URL}{config.AUTH}{config.EMAIL_VERIFICATION}/{auth_data["token"].decode()}', time = expiriy['time'])
#         print(email_payload)
#         print(email_payload.dict())
#         # mail_notify(user.email, EMAIL_VERIFICATION, email_payload)

#     except:
#         raise InternalServerErrorException("Something went wrong sending verification mail")

# # def send_invitation_mail(invitation: BaseInvitation, company_name: str = None, expiriy: dict = EmailTokenExp(time='48 hours', seconds=172800).__dict__):
# #     auth_data = {"token":TokenHelper.encode(jsonable_encoder(BaseInvitation.from_orm(invitation)), expiriy["seconds"])}
# #     email_payload = InvitationEmail(first_name = invitation.sender.first_name, last_name = invitation.sender.last_name, company_name=company_name, action_url = f'{config.CLIENT_CANDIDATE_BASE_URL}{config.AUTH}{config.ACCEPT_INVITATION}/{auth_data["token"].decode()}', time = expiriy['time'])
# #     mail_notify(invitation.addressee, CLIENT_INVITATION, email_payload)
    
