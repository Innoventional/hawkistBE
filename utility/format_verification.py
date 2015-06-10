import re
import datetime
from environment import env

__author__ = 'ne_luboff'


def phone_verification(phone):
    phone = str(phone)
    phone = phone.replace('+', '')
    try:
        int(phone)
    except:
        return 'Invalid number format. Example: 14697063609'

    if len(phone) < 10:
        return 'Phone number must contain at least 10 digits (country code, operator code and phone number)'
    return False


def username_verification(username):
    if not re.match('^\w[\w.-]+$', username.decode('utf-8'), re.U):
        return 'Username can consist of string, digits, dash symbols and dots'
    return False


def email_verification(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return 'Invalid email format. Example: your@mail.com'
    return False


# check user avability to send one more sms
def sms_limit_check(self):
    if self.user.last_pin_sending:
        if self.user.sent_pins_count >= env['sms_limit_per_hour']:
            available_time = self.user.last_pin_sending + datetime.timedelta(hours=1)
            current_time = datetime.datetime.utcnow()
            if current_time < available_time:
                return 'You sent sms 3 times per hour. Try again later'
            else:
                self.user.sent_pins_count = 0
    else:
        self.user.sent_pins_count = 0
    self.session.commit()
    return False
