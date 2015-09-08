# -*- coding: utf-8 -*-
import re
import datetime
from environment import env
from ui_messages.errors.utility_errors.format_verification_errors import PHONE_VERIFICATION_NOT_DIGITS_ONLY, \
    PHONE_VERIFICATION_TOO_SHORT_NUMBER, PHONE_VERIFICATION_TOO_LONG_NUMBER, EMAIL_VERIFICATION_INVALID_FORMAT, \
    USERNAME_VERIFICATION_TOO_LONG_USERNAME, USERNAME_VERIFICATION_INVALID_FORMAT
from ui_messages.errors.utility_errors.twilio_api_errors import TWILIO_RICH_SMS_LIMIT

__author__ = 'ne_luboff'


def phone_verification(phone):
    """
    Phone verification.
    We must replaced plus sign.
    Check minimum and maximum length of number and is this number contains only of digits.
    """
    phone = str(phone)
    phone = phone.replace('+', '')
    try:
        int(phone)
    except:
        return PHONE_VERIFICATION_NOT_DIGITS_ONLY

    if len(phone) < 10:
        return PHONE_VERIFICATION_TOO_SHORT_NUMBER

    if len(phone) > 15:
        return PHONE_VERIFICATION_TOO_LONG_NUMBER
    return False


def phone_reformat(phone):
    """
    Pre-processing for Great Britain numbers.
    If mobile number started with 07 we must change it to 447.
    """
    if str(phone[0:2]) == '07':
        phone = phone.replace('0', '44', 1)
    return phone


def username_verification(username):
    """
    Username verification.
    Usernames can consist of chars, digits, dots and dashes only.
    """
    if len(username) > 50:
        return USERNAME_VERIFICATION_TOO_LONG_USERNAME
    if not re.match('^\w[\w-]*$', username.decode('utf-8'), re.U):
        return USERNAME_VERIFICATION_INVALID_FORMAT
    return False


def email_verification(email):
    """
    Verification for email format.
    Valid email address example: test_email@mail.com.
    """
    if not re.match(r"^([\w+_\.-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$", email.decode('utf-8'), re.U):
        return EMAIL_VERIFICATION_INVALID_FORMAT
    return False


def sms_limit_check(self):
    """
    Check does current user reach sms limit per hour.
    Standard sms limit count - 3.
    """
    if not self.user:
        return False
    if self.user.last_pin_sending:
        if self.user.sent_pins_count >= env['sms_limit_per_hour']:
            available_time = self.user.last_pin_sending + datetime.timedelta(hours=1)
            current_time = datetime.datetime.utcnow()
            if current_time < available_time:
                return TWILIO_RICH_SMS_LIMIT % env['sms_limit_per_hour']
            else:
                self.user.sent_pins_count = 0
    else:
        self.user.sent_pins_count = 0
    self.session.commit()
    return False