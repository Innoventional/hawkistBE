__author__ = 'ne_luboff'

"""
Sign up
"""
# empty phone and facebook token
SIGN_UP_EMPTY_AUTHORIZATION_DATA = 'Empty authorisation data'

"""
Log in (in case if user sign up using phone number)
"""
# empty phone or pin
LOG_IN_EMPTY_AUTHORIZATION_DATA = 'You must input a mobile number and a pin code to sign in.'

# if user enter phone number of unexisting user
LOG_IN_USER_NOT_FOUND = 'There is no user with mobile number %s. Please check the mobile number or sign up.'

# if user enter wrong pin
LOG_IN_INCORRECT_PIN = 'The pin %s is incorrect. Please try again or request a new pin.'
