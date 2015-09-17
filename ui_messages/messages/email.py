# -*- coding: utf-8 -*-
__author__ = 'ne_luboff'

# confirm email letter
CONFIRM_EMAIL_LETTER_SUBJECT = 'Email Confirmation Required'
CONFIRM_EMAIL_LETTER_TEXT = '<b>%s</b>,<br/><br/>' \
                            'To complete your Hawkist account we need you to confirm this email address.<br/>' \
                            '<a href="%s/api/user/confirm_email/%s">Please follow this link.</a><br/><br/>' \
                            'Thanks,<br/><br/>' \
                            'Hawkist'

CONFIRM_SUCCESS_EMAIL_LETTER_SUBJECT = 'Hawkist Account is Ready'
CONFIRM_SUCCESS_EMAIL_LETTER_TEXT = "<b>%s</b>,<br/><br/>" \
                                    "Thanks for confirming your email address. Your Hawkist account is now ready to go!<br/><br/>" \
                                    "Don't forget to connect your Facebook profile to Hawkist in order to maximise your " \
                                    "chances of selling an item.<br/><br/>" \
                                    "Hawkist<br/><br/>" \
                                    "<a href='https://www.facebook.com/hawkistUK'>Follow us on Facebook</a><br/><br/>" \
                                    "<a href='https://twitter.com/HawkistUK'>Follow us on Twitter</a>"

# change user group
ADMIN_BACK_USER_TO_STANDARD_USERTYPE_LETTER_TEXT = 'Looks like you were excluded from Hawkist %s user group.'
ADMIN_CHANGE_USERTYPE_LETTER_TEXT = 'Congrats!<br/><br/>' \
                                    'You were added to Hawkist %s user group. Go to %s and use your email ' \
                                    'address and this temporary password to log in administration module:<br/>%s<br/>Enjoy!'
ADMIN_CHANGE_USERTYPE_LETTER_SUBJECT = 'Permissions changed'

# change user phone number
ADMIN_PHONE_NUMBER_CHANGED_LETTER_TEXT = '<b>%s</b>,<br/><br/>' \
                                         'Your mobile number was recently updated to <b>%s</b>. If you have any ' \
                                         'questions, please contact us on info@hawkist.com.<br/><br/>' \
                                         'Thanks,<br/><br/>' \
                                         'Hawkist'
ADMIN_PHONE_NUMBER_CHANGED_LETTER_SUBJECT = 'Mobile Number has been Changed'

ADMIN_EMAIL_CHANGED_LETTER_TEXT = '<b>%s</b>,<br/><br/>' \
                                  'Your email address was recently updated. If you have any questions, please contact ' \
                                  'us on info@hawkist.com.<br/><br/>' \
                                  'Thanks,<br/><br/>' \
                                  'Hawkist'
ADMIN_EMAIL_CHANGED_LETTER_SUBJECT = 'Email Address has been Changed'

# suspend account
ADMIN_ACCOUNT_SUSPENDED_TEXT = 'Dear <b>%s</b>,<br/><br/>' \
                               'Unfortunately your Hawkist account has been suspended. If you believe this to be a ' \
                               'mistake, please contact Hawkist support on info@hawkist.com.'
ADMIN_ACCOUNT_SUSPENDED_SUBJECT = 'Hawkist Account Suspended'

ADMIN_ACCOUNT_ACTIVATED_TEXT = 'Dear <b>%s</b>,<br/><br/>' \
                               'Your Hawkist account has been reactivated. Please contact Hawkist support on ' \
                               'info@hawkist.com if you have any other questions<br/><br/>' \
                               'Thanks<br/><br/>' \
                               'Hawkist Support'
ADMIN_ACCOUNT_ACTIVATED_SUBJECT = 'Hawkist Account Reactivated'

# PAYMENTS
PURCHASE_ITEM_BUYER_TITLE = '%s'
PURCHASE_ITEM_BUYER_TEXT = u'<b>%s</b>,<br/>' \
                           u'You recently purchased <b>%s</b> for <b>£%s</b> from <b>%s</b>. This email is confirmation ' \
                           u'that we have taken payment for the item.<br/><br/>' \
                           u'Please note that you have 7 days to confirm receipt of the item to us or indicate any ' \
                           u'issues with it before we release your payment to the seller.<br/><br/>' \
                           u'If you need to contact the seller for any reason, please use their email address which ' \
                           u'is %s. However, we have left instructions for them to ship the item as soon as ' \
                           u'possible.<br/><br/>' \
                           u'For more information about returns or refunds, please visit our FAQs on ' \
                           u'https://hawkist.zendesk.com.<br/><br/>' \
                           u'If you have any questions, you can contact Hawkist support on info@hawkist.com.<br/><br/>' \
                           u'Thanks for your business!<br/><br/>' \
                           u'Hawkist'

PURCHASE_ITEM_SELLER_TITLE = 'Sold: %s'
PURCHASE_ITEM_SELLER_TEXT = u"<b>%s</b>,<br/><br/>" \
                            u"Your item <b>%s</b> has been sold to <b>%s</b> for <b>£%s</b>. The next step is for you " \
                            u"to arrange delivery or collection of the item. The buyer can be contacted via email " \
                            u"on %s.<br/><br/>" \
                            u"Please note that you now have 7 days to arrange for delivery or collection of the item " \
                            u"before we can release your funds. The faster %s gets the item, the faster " \
                            u"you get the funds.<br/><br/>" \
                            u"For more information about receiving funds after a purchase, please visit our FAQs on " \
                            u"https://hawkist.zendesk.com.<br/><br/>" \
                            u"If you have any questions, you can contact Hawkist support on info@hawkist.com.<br/><br/>" \
                            u"Thanks for your business!<br/><br/>" \
                            u"Hawkist"

PURCHASE_ITEM_SELLER_TEXT_WITH_ADDRESS = u"<b>%s</b>,<br/><br/>" \
                                         u"Your item <b>%s</b> has been sold to <b>%s</b> for <b>£%s</b>. The next " \
                                         u"step is for you to arrange delivery or collection of the item. The buyer " \
                                         u"can be contacted via email on %s.<br/><br/>" \
                                         u"His delivery address is %s.<br/><br/>" \
                                         u"Please note that you now have 7 days to arrange for delivery or collection " \
                                         u"of the item before we can release your funds. The faster %s gets the item, " \
                                         u"the faster you get the funds.<br/><br/>" \
                                         u"For more information about receiving funds after a purchase, please visit " \
                                         u"our FAQs on https://hawkist.zendesk.com.<br/><br/>" \
                                         u"If you have any questions, you can contact Hawkist support on " \
                                         u"info@hawkist.com.<br/><br/>" \
                                         u"Thanks for your business!<br/><br/>" \
                                         u"Hawkist"

LISTING_WITH_ISSUE_SELLER_TITLE = 'Has issue: %s'
LISTING_WITH_ISSUE_SELLER_TEXT = '<b>%s</b>,<br/><br/>' \
                                 'Your item <b>%s</b> has been marked with an issue by <b>%s</b>. A support ticket ' \
                                 'has been opened in order to investigate.<br/><br/>' \
                                 'Please note that we will be unable to the release the funds for this item until our ' \
                                 'investigation is complete.<br/><br/>' \
                                 'For more information about why Hawkist is holding your funds, please visit our ' \
                                 'FAQs on https://hawkist.zendesk.com.<br/><br/>' \
                                 'If you have any questions, you can contact Hawkist support on info@hawkist.com.<br/><br/>' \
                                 'Thanks for your business!<br/><br/>' \
                                 'Hawkist'

LISTING_RECEIVED_SELLER_TITLE = 'Received: %s'
LISTING_RECEIVED_SELLER_TEXT = u"<b>%s</b>,<br/><br/>" \
                               u"Your item <b>%s</b> has been marked received by <b>%s</b>. We have now released the " \
                               u"funds for this order into your Hawkist wallet.<br/><br/>" \
                               u"Please note that Hawkist charges a fee for successful transactions so you will " \
                               u"be receiving <b>£%s</b>.<br/><br/>" \
                               u"For more information about our charges, please visit our FAQs on " \
                               u"https://hawkist.zendesk.com.<br/><br/>" \
                               u"If you have any questions, you can contact Hawkist support on info@hawkist.com.<br/><br/>" \
                               u"Thanks for your business!<br/><br/>" \
                               u"Hawkist"


LISTING_WITH_ISSUE_INVESTIGATION_OPENED_TITLE = 'Investigation Opened: %s'
LISTING_WITH_ISSUE_INVESTIGATION_OPENED_TEXT = "<b>%s</b>,<br/><br/>" \
                                               "You indicated there were issues with your recent purchase of <b>%s</b>. " \
                                               "As a result, a support ticket has been opened in order to investigate " \
                                               "these issues. We will shortly be contacting you via email to gather more " \
                                               "information.<br/><br/>" \
                                               "Please note that we have not released your payment to the seller and " \
                                               "will not do so until the investigation completed.<br/><br/>" \
                                               "For more information about how Hawkist investigates issues with " \
                                               "purchases, please visit our FAQs on https://hawkist.zendesk.com.<br/><br/>" \
                                               "If you have any questions, you can contact Hawkist support on " \
                                               "info@hawkist.com.<br/><br/>" \
                                               "Thanks for your business!<br/><br/>" \
                                               "Hawkist"


FUNDS_RECEIVED_SELLER_TITLE = 'Funds Received: %s'
FUNDS_RECEIVED_SELLER_TEXT = u"<b>%s</b>,<br/><br/>" \
                             u"We have now released the funds for your item <b>%s</b> into your Hawkist wallet.<br/><br/>" \
                             u"Please note that Hawkist charges a fee for successful transactions so you will be " \
                             u"receiving <b>£%s</b>.<br/><br/>" \
                             u"For more information about our charges, please visit our FAQs on " \
                             u"https://hawkist.zendesk.com.<br/><br/>" \
                             u"If you have any questions, you can contact Hawkist support on info@hawkist.com.<br/><br/>" \
                             u"Thanks for your business!<br/><br/>" \
                             u"Hawkist"

TRANSACTION_CANCELED_TITLE = 'Cancelled: %s'
TRANSACTION_CANCELED_TEXT = '<b>%s</b>,<br/><br/>' \
                            'After conducting a thorough investigation into the issues on <b>%s</b> we have concluded ' \
                            'the order should be cancelled.<br/><br/>' \
                            'Please note that a refund will shortly be issued.<br/><br/>' \
                            'For more information about cancellations and refunds, please visit our FAQs on ' \
                            'https://hawkist.zendesk.com.<br/><br/>' \
                            'If you have any questions, you can contact Hawkist support on info@hawkist.com.<br/><br/>' \
                            'Thanks for your business<br/><br/>' \
                            'Hawkist'

REFUND_ISSUES_BUYER_TITLE = 'Refund: %s'
REFUND_ISSUES_BUYER_TEXT = u"<b>%s</b>,<br/><br/>" \
                           u"A refund has been issued for your recent purchase of <b>%s</b>. We have credited your " \
                           u"Hawkist wallet with <b>£%s</b>.<br/><br/>" \
                           u"For more information about cancellations and refunds, please visit our FAQs on " \
                           u"https://hawkist.zendesk.com.<br/><br/>" \
                           u"If you have any questions, you can contact Hawkist support on info@hawkist.com.<br/><br/>" \
                           u"Thanks for your business!<br/><br/>" \
                           u"Hawkist"

INVESTIGATION_RESOLVED_TITLE = 'Resolved: %s'
INVESTIGATION_RESOLVED_TEXT = '<b>%s</b>,<br/><br/>' \
                              'After conducting a thorough investigation into the issues on <b>%s</b> we have decided ' \
                              'that the order will proceed.<br/><br/>' \
                              'Please note that funds will not be refunded.<br/><br/>' \
                              'For more information about how Hawkist investigates issues with purchases, please visit ' \
                              'our FAQs on https://hawkist.zendesk.com.<br/><br/>' \
                              'If you have any questions, you can contact Hawkist support on info@hawkist.com.<br/><br/>' \
                              'Thanks for your business!<br/><br/>' \
                              'Hawkist'

HAS_ITEM_RECEIVED_TITLE = 'Update Required: %s'
HAS_ITEM_RECEIVED_TEXT = '<b>%s</b>,<br/><br/>' \
                         'It has been <b>%s</b> days since you purchased <b>%s</b>. Has the item arrived yet?<br/><br/>' \
                         'If so please log on to Hawkist and let us know. We need an update so the payment for this ' \
                         'purchase can be released to the seller.<br/><br/>' \
                         'For more information about how to update orders, please visit our FAQs on ' \
                         'https://hawkist.zendesk.com.<br/><br/>' \
                         'If you have any questions, you can contact Hawkist support on info@hawkist.com.<br/><br/>' \
                         'Thanks for your business!<br/><br/>' \
                         'Hawkist'


WITHDRAWAL_REQUESTED_TITLE = 'Withdrawal Request Received'
WITHDRAWAL_REQUESTED_TEXT = u'<b>%s</b>,<br/><br/>' \
                            u'We have received your request to withdraw <b>£%s</b> from your Hawkist account. We will ' \
                            u'contact you once the money has been transferred to your bank account.<br/><br/>' \
                            u'For more information about withdrawing your account balance, please visit our FAQs on ' \
                            u'https://hawkist.zendesk.com.<br/><br/>' \
                            u'If you have any questions, you can contact Hawkist support on info@hawkist.com.<br/><br/>' \
                            u'Thanks for your business!<br/><br/>' \
                            u'Hawkist'

WITHDRAWAL_COMPLETED_TITLE = 'Withdrawal Request Processed'
WITHDRAWAL_COMPLETED_TEXT = u'<b>%s</b>,<br/><br/>' \
                            u'We have now processed your withdrawal request for <b>£%s</b>. The money is available ' \
                            u'in your bank account.<br/><br/>' \
                            u'For more information about withdrawing your account balance, please visit our FAQs ' \
                            u'on https://hawkist.zendesk.com.<br/><br/>' \
                            u'If you have any questions, you can contact Hawkist support on info@hawkist.com.<br/><br/>' \
                            u'Thanks for your business!<br/><br/>' \
                            u'Hawkist'


