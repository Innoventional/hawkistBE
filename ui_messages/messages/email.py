# -*- coding: utf-8 -*-
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

# PAYMENTS
PURCHASE_ITEM_BUYER_TITLE = '%s'
PURCHASE_ITEM_BUYER_TEXT = u"%s,\n" \
                           u"You recently purchased %s for £%s from %s. This email is confirmation that we have taken " \
                           u"payment for the item.\n" \
                           u"In order to contact the seller, please use their email address which is %s.\n" \
                           u"Please note that you have 7 days to confirm receipt of the item to us or indicate any " \
                           u"issues with it before we release your funds to the seller." \
                           u"For more information about returns or refunds, please visit our FAQs on " \
                           u"https://hawkist.zendesk.com." \
                           u"If you have any questions, you can contact Hawkist support on info@hawkist.com.\n" \
                           u"Thanks for your business!\n" \
                           u"Hawkist"

PURCHASE_ITEM_SELLER_TITLE = 'Sold: %s'
PURCHASE_ITEM_SELLER_TEXT = "%s,\n" \
                            u"Your item %s has been sold to %s for £%s. The next step is for you to arrange delivery or " \
                            u"collection of the item. The buyer can be contacted via email on %s.\n" \
                            u"His delivery address is BUYER_DELIVERY_ADDRESS_NEXT_SPRINT." \
                            u"Please note that you now have 7 days to arrange for delivery or collection of the item " \
                            u"before we can release your funds. The faster %s gets the item, the faster " \
                            u"you get the funds.\n" \
                            u"For more information about receiving funds after a purchase, please visit our FAQs on " \
                            u"https://hawkist.zendesk.com.\n" \
                            u"If you have any questions, you can contact Hawkist support on info@hawkist.com.\n" \
                            u"Thanks for your business!\n" \
                            u"Hawkist"

LISTING_WITH_ISSUE_SELLER_TITLE = 'Has issue: %s'
LISTING_WITH_ISSUE_SELLER_TEXT = '%s,\n' \
                                 'Your item %s has been marked with an issue by %s. A support ticket has been opened in ' \
                                 'order to investigate.\n' \
                                 'Please note that we will be unable to the release the funds for this item until our ' \
                                 'investigation is complete.\n' \
                                 'For more information about why Hawkist is holding your funds, please visit our ' \
                                 'FAQs on https://hawkist.zendesk.com.\n' \
                                 'If you have any questions, you can contact Hawkist support on info@hawkist.com.\n' \
                                 'Thanks for your business!\n' \
                                 'Hawkist'

LISTING_RECEIVED_SELLER_TITLE = 'Received: %s'
LISTING_RECEIVED_SELLER_TEXT = "%s,\n" \
                               u"Your item %s has been marked received by %s. We have now released the funds for this " \
                               u"order into your Hawkist wallet.\n" \
                               u"Please note that Hawkist charges a fee for successful transactions so you will " \
                               u"be receiving £%s.\n" \
                               u"For more information about our charges, please visit our FAQs on " \
                               u"https://hawkist.zendesk.com.\n" \
                               u"If you have any questions, you can contact Hawkist support on info@hawkist.com.\n" \
                               u"Thanks for your business!\n" \
                               u"Hawkist"


LISTING_WITH_ISSUE_INVESTIGATION_OPENED_TITLE = 'Investigation Opened: %s'
LISTING_WITH_ISSUE_INVESTIGATION_OPENED_TEXT = "%s,\n" \
                                               "You indicated there were issues with your recent purchase of %s. " \
                                               "As a result, a support ticket has been opened in order to investigate " \
                                               "these issues. We will shortly be contacting you via email to gather more " \
                                               "information.\n" \
                                               "Please note that we have not released your payment to the seller and " \
                                               "will not do so until the investigation completed.\n" \
                                               "For more information about how Hawkist investigates issues with " \
                                               "purchases, please visit our FAQs on https://hawkist.zendesk.com.\n" \
                                               "If you have any questions, you can contact Hawkist support on " \
                                               "info@hawkist.com.\n" \
                                               "Thanks for your business!\n" \
                                               "Hawkist"


FUNDS_RECEIVED_SELLER_TITLE = 'Funds Received: %s'
FUNDS_RECEIVED_SELLER_TEXT = u"%s,\n" \
                             u"We have now released the funds for your item %s into your Hawkist wallet.\n" \
                             u"Please note that Hawkist charges a fee for successful transactions so you will be " \
                             u"receiving £%s.\n" \
                             u"For more information about our charges, please visit our FAQs on " \
                             u"https://hawkist.zendesk.com.\n" \
                             u"If you have any questions, you can contact Hawkist support on info@hawkist.com.\n" \
                             u"Thanks for your business!\n" \
                             u"Hawkist"

TRANSACTION_CANCELED_TITLE = 'Cancelled: %s'
TRANSACTION_CANCELED_TEXT = '%s,\n' \
                            'After conducting a thorough investigation into the issues on %s we have concluded the ' \
                            'order should be cancelled.\n' \
                            'Please note that a refund will shortly be issued.\n' \
                            'For more information about cancellations and refunds, please visit our FAQs on ' \
                            'https://hawkist.zendesk.com.\n' \
                            'If you have any questions, you can contact Hawkist support on info@hawkist.com.\n' \
                            'Thanks for your business\n' \
                            'Hawkist'

REFUND_ISSUES_BUYER_TITLE = 'Refund: %s'
REFUND_ISSUES_BUYER_TEXT = u"%s,\n" \
                           u"A refund has been issued for your recent purchase of %s. We have credited your Hawkist " \
                           u"wallet with £%s.\n" \
                           u"For more information about cancellations and refunds, please visit our FAQs on " \
                           u"https://hawkist.zendesk.com.\n" \
                           u"If you have any questions, you can contact Hawkist support on info@hawkist.com.\n" \
                           u"Thanks for your business!\n" \
                           u"Hawkist"

INVESTIGATION_RESOLVED_TITLE = 'Resolved: %s'
INVESTIGATION_RESOLVED_TEXT = '%s,\n' \
                              'After conducting a thorough investigation into the issues on %s we have decided that the ' \
                              'order will proceed.\n' \
                              'Please note that funds will not be refunded.\n' \
                              'For more information about how Hawkist investigates issues with purchases, please visit ' \
                              'our FAQs on https://hawkist.zendesk.com.\n' \
                              'If you have any questions, you can contact Hawkist support on info@hawkist.com.\n' \
                              'Thanks for your business!\n' \
                              'Hawkist'

HAS_ITEM_RECEIVED_TITLE = 'Has received: %s'
HAS_ITEM_RECEIVED_TEXT = '%s,\n' \
                         'Do we send an email to a buyer if he does not confirm receipt of an item within 7 days and ' \
                         'funds are automatically released to the seller?\n' \
                         'Thanks for your business!\n' \
                         'Hawkist'


