# -*- coding: utf-8 -*-
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
        return 'Invalid number format. Digits only'

    if len(phone) < 10:
        return 'Phone number must contain at least 10 digits (country code, operator code and phone number)'

    if len(phone) > 15:
        return 'Phone number to long. Maximum length - 15 digits'
    return False


def username_verification(username):
    if len(username) > 50:
        return 'Too long username. Max length - 50 symbols'
    if not re.match('^\w[\w\s.-]+$', username.decode('utf-8'), re.U):
        return 'Username can consist of string, digits, dash symbols and dots'
    return False


def email_verification(email):
    if not re.match(r"^([\w+_\.-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$", email.decode('utf-8'), re.U):
        return 'Invalid email format. Example: your@mail.com'
    return False


# check user avability to send one more sms
def sms_limit_check(self):
    if not self.user:
        return False
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
