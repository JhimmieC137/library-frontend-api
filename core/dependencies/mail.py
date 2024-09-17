from enum import Enum
from core.helpers.schemas import EmailParameters
from core.exceptions.base import BadRequestException
from postmark.core import PMMail, PMMailSendException

from core.env import config

SENDER_MAIL = ""
API_KEY = config.POSTMARK_API_KEY

# class MailTemplate(Enum.enum): 
#    CANDIDATE_WELCOME = 32648890
#     CLIENT_WELCOME = 32648890

class EmailSender:
    @staticmethod
    def send_mail(payload: EmailParameters):
        try: 
            pm = PMMail(api_key=API_KEY,
                        to=payload.recipient_mail, 
                        sender=SENDER_MAIL,
                        template_id=payload.template_id, 
                        template_model=payload.template_values)
            pm.send()
        except: 
            raise BadRequestException("Invalid email address or error connecting to mail engine")
        
    