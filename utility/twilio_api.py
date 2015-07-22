import logging
import requests
from twilio.rest import TwilioRestClient, exceptions
from ui_messages.errors.utility_errors.twilio_api_errors import TWILIO_INVALID_PHONE_NUMBER, TWILIO_UNSUPPORTED_REGION

logger = logging.getLogger(__name__)

__author__ = 'ne_luboff'

# account_sid = "ACbc4b5aa87ac7329916beac9cd197b438"
# auth_token = "0011bf9dbbde88c80430fa227852294f"
# from_number = "+14697063609"

# consumer twilio live account credentials
account_sid = "AC21a1e1681c5c5a07068883a237a4084f"
auth_token = "acee56df48b9700fa65966262275c041"
from_number = "Hawkist"
# from_number = "+447903596742"


def send_sms(to_number, text):
    error = ''
    try:
        client = TwilioRestClient(account_sid, auth_token)
        message = client.messages.create(to="+" + to_number, from_=from_number, body=text)
        url = "https://api.twilio.com/2010-04-01/Accounts/{0}/Messages".format(account_sid)
        r = requests.post(url)
    except exceptions.TwilioRestException, e:
        exception_text = str(e)
        if 'is not a valid phone number' in exception_text:
            logger.debug('https://www.twilio.com/docs/errors/21211')
            error = TWILIO_INVALID_PHONE_NUMBER
        if 'Permission to send an SMS has not been enabled for the region' in exception_text:
            logger.debug('https://www.twilio.com/docs/errors/21408')
            error = TWILIO_UNSUPPORTED_REGION
    finally:
        return error

if __name__ == '__main__':
    # print send_sms("380937181958", 'test')
    print send_sms("07446263710", 'test')

