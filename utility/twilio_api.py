import logging
import requests
from twilio.rest import TwilioRestClient, exceptions

logger = logging.getLogger(__name__)

__author__ = 'ne_luboff'

account_sid = "ACbc4b5aa87ac7329916beac9cd197b438"
auth_token = "0011bf9dbbde88c80430fa227852294f"
from_number = "+14697063609"


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
            error = 'Invalid number format. Example: 14697063609'
        if 'Trial accounts cannot send messages to unverified numbers' in exception_text:
            logger.debug('https://www.twilio.com/docs/errors/21608')
            error = 'Trial accounts cannot send messages to unverified numbers. Ask account owner verify your number ' \
                    'or ask consumer purchase a Twilio number to send messages to unverified numbers'
        if 'Permission to send an SMS has not been enabled for the region' in exception_text:
            logger.debug('https://www.twilio.com/docs/errors/21408')
            error = 'Permission to send an SMS has not been enabled for your region. Ask Twilio account owner add ' \
                    'your country to supported list'
    finally:
        return error

if __name__ == '__main__':
    print send_sms("380993351739", 'test')

