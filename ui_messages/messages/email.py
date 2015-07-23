__author__ = 'ne_luboff'

# confirm email letter
CONFIRM_EMAIL_LETTER_SUBJECT = 'Email Confirmation Required'
CONFIRM_EMAIL_LETTER_TEXT = '%s,\n' \
                            'To complete your Hawkist account we need you to confirm this email address.\n' \
                            'Please follow this link:\n' \
                            '%s/api/user/confirm_email/%s\n' \
                            'Thanks,\n' \
                            'Hawkist'

CONFIRM_SUCCESS_EMAIL_LETTER_SUBJECT = 'Hawkist Account is Ready'
CONFIRM_SUCCESS_EMAIL_LETTER_TEXT = "%s,\n" \
                                    "Thanks for confirming your email address. Your Hawkist account is now ready to go!\n" \
                                    "Don't forget to connect your Facebook profile to Hawkist in order to maximise your " \
                                    "chances of selling an item.\n" \
                                    "Hawkist\n" \
                                    "Follow us on Facebook\n" \
                                    "Follow us on Twitter"

# change user group
ADMIN_BACK_USER_TO_STANDARD_USERTYPE_LETTER_TEXT = 'Looks like you were excluded from Hawkist %s user group.'
ADMIN_CHANGE_USERTYPE_LETTER_TEXT = 'Congrats!\nYou were added to Hawkist %s user group. Go to %s and use your email ' \
                                    'address and this temporary password to log in administration module:\n%s\nEnjoy!'
ADMIN_CHANGE_USERTYPE_LETTER_SUBJECT = 'Permissions changed'

# change user phone number
ADMIN_PHONE_NUMBER_CHANGED_LETTER_TEXT = '%s,\n' \
                                         'Your mobile number was recently updated to %s. If you have any questions, ' \
                                         'please contact us on info@hawkist.com.\n' \
                                         'Thanks,\n' \
                                         'Hawkist'
ADMIN_PHONE_NUMBER_CHANGED_LETTER_SUBJECT = 'Mobile Number has been Changed'

ADMIN_EMAIL_CHANGED_LETTER_TEXT = '%s,\n' \
                                  'Your email address was recently updated. If you have any questions, please contact ' \
                                  'us on info@hawkist.com.\n' \
                                  'Thanks,\n' \
                                  'Hawkist'
ADMIN_EMAIL_CHANGED_LETTER_SUBJECT = 'Email Address has been Changed'

# suspend account
ADMIN_ACCOUNT_SUSPENDED_TEXT = 'Dear %s,\n' \
                               'Unfortunately your Hawkist account has been suspended. If you believe this to be a ' \
                               'mistake, please contact Hawkist support on info@hawkist.com.'
ADMIN_ACCOUNT_SUSPENDED_SUBJECT = 'Hawkist Account Suspended'

ADMIN_ACCOUNT_ACTIVATED_TEXT = 'Dear %s,\n' \
                               'Your Hawkist account has been reactivated. Please contact Hawkist support on ' \
                               'info@hawkist.com if you have any other questions\n' \
                               'Thanks\n' \
                               'Hawkist Support'
ADMIN_ACCOUNT_ACTIVATED_SUBJECT = 'Hawkist Account Reactivated'
