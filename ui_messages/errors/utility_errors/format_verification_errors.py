__author__ = 'ne_luboff'

"""
Phone number verification
"""
PHONE_VERIFICATION_NOT_DIGITS_ONLY = 'Invalid number format. Digits only'
PHONE_VERIFICATION_TOO_SHORT_NUMBER = 'Phone number must contain at least 10 digits (country code, operator code and ' \
                                      'phone number)'
PHONE_VERIFICATION_TOO_LONG_NUMBER = 'Phone number too long. Maximum length - 15 digits'

"""
Email address verification
"""
EMAIL_VERIFICATION_INVALID_FORMAT = 'Invalid email format. Example: your@mail.com'

"""
Username verification
"""
USERNAME_VERIFICATION_TOO_LONG_USERNAME = 'Too long username. Max length - 50 symbols'
USERNAME_VERIFICATION_INVALID_FORMAT = 'Username can consist of string, digits, dash symbols and dots'
