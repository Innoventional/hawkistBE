from email.mime.multipart import MIMEMultipart
import logging
import smtplib
from email.mime.text import MIMEText
from environment import env
from helpers import encrypt_password
from ui_messages.messages.email import CONFIRM_EMAIL_LETTER_SUBJECT, CONFIRM_EMAIL_LETTER_TEXT, \
    PURCHASE_ITEM_BUYER_TITLE, PURCHASE_ITEM_BUYER_TEXT, PURCHASE_ITEM_SELLER_TITLE, PURCHASE_ITEM_SELLER_TEXT, \
    LISTING_WITH_ISSUE_SELLER_TEXT, LISTING_WITH_ISSUE_SELLER_TITLE, LISTING_WITH_ISSUE_INVESTIGATION_OPENED_TITLE, \
    LISTING_WITH_ISSUE_INVESTIGATION_OPENED_TEXT, LISTING_RECEIVED_SELLER_TITLE, LISTING_RECEIVED_SELLER_TEXT, \
    FUNDS_RECEIVED_SELLER_TITLE, FUNDS_RECEIVED_SELLER_TEXT, TRANSACTION_CANCELED_TITLE, TRANSACTION_CANCELED_TEXT, \
    REFUND_ISSUES_BUYER_TEXT, REFUND_ISSUES_BUYER_TITLE, INVESTIGATION_RESOLVED_TITLE, INVESTIGATION_RESOLVED_TEXT, \
    HAS_ITEM_RECEIVED_TITLE, HAS_ITEM_RECEIVED_TEXT, PURCHASE_ITEM_SELLER_TEXT_WITH_ADDRESS, WITHDRAWAL_REQUESTED_TITLE, \
    WITHDRAWAL_REQUESTED_TEXT, WITHDRAWAL_COMPLETED_TITLE, WITHDRAWAL_COMPLETED_TEXT

__author__ = 'ne_luboff'


logger = logging.getLogger(__name__)

# for bold text
BOLD_STRING = '\033[1m%s\033[0m'


def send_email(text=None, subject=None, recipient=None, filename=None, recipients=None, html=None, template_name=None,
               from_email=None, **kwargs):
    msg = MIMEMultipart('alternative')
    if subject is None:
        subject = env['mail']['subject']

    if from_email is None:
        from_email = env['mail']['from']

    text = text.encode('utf-8')
    subject = subject.encode('utf-8')
    from_email = from_email.encode('utf-8')
    recipient = recipient.encode('utf-8')

    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = recipient

    if text:
        part1 = MIMEText(text, 'plain')
        msg.attach(part1)


    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    server = smtplib.SMTP(env['mail']['server'], env['mail']['port'])
    server.ehlo()

    login = env['mail']['login']
    password = env['mail']['password']

    if login is not None and password is not None:
        server.starttls()
        server.login(login, password)

    recipients = recipients if recipients else [recipient, ]
    print server.sendmail(env['mail']['from'], recipients, msg.as_string())
    logger.debug('Message to %s send successfully' % recipient)
    logger.debug(text)
    server.quit()


def email_confirmation_sending(self, user, email):
    # create salt as email + user id
    email_salt = encrypt_password(password=email+str(user.id), salt=env['password_salt'])
    user.email_salt = email_salt
    self.session.commit()

    text = CONFIRM_EMAIL_LETTER_TEXT % (user.username, env['server_address'], email_salt)
    subject = CONFIRM_EMAIL_LETTER_SUBJECT
    send_email(text, subject=subject, recipient=email)


def purchase_confirmation_sending_buyer(self, listing):
    text = PURCHASE_ITEM_BUYER_TEXT % (self.user.username, BOLD_STRING % listing.title,
                                       "%.02f" % float(listing.selling_price), listing.user.username,
                                       listing.user.email)
    subject = PURCHASE_ITEM_BUYER_TITLE % listing.title
    send_email(text, subject=subject, recipient=self.user.email)


def purchase_confirmation_sending_seller(self, listing, address):
    if address:
        address_row = '%s, %s %s' % (address.address_line1, address.postcode, address.city)
        if address.address_line2:
            address_row = '%s %s, %s %s' % (address.address_line1, address.address_line2, address.postcode,
                                            address.city)
        text = PURCHASE_ITEM_SELLER_TEXT_WITH_ADDRESS % (listing.user.username, BOLD_STRING % listing.title,
                                                         self.user.username, "%.02f" % float(listing.selling_price),
                                                         self.user.email, address_row, self.user.username)
    else:
        text = PURCHASE_ITEM_SELLER_TEXT % (listing.user.username, BOLD_STRING % listing.title, self.user.username,
                                            "%.02f" % float(listing.selling_price), self.user.email, self.user.username)
    subject = PURCHASE_ITEM_SELLER_TITLE % listing.title
    send_email(text, subject=subject, recipient=listing.user.email)


def listing_with_issue_seller(self, listing):
    text = LISTING_WITH_ISSUE_SELLER_TEXT % (listing.user.username, BOLD_STRING % listing.title, self.user.username)
    subject = LISTING_WITH_ISSUE_SELLER_TITLE % listing.title
    send_email(text, subject=subject, recipient=listing.user.email)


def listing_received_seller(self, order):
    text = LISTING_RECEIVED_SELLER_TEXT % (order.listing.user.username, BOLD_STRING % order.listing.title,
                                           self.user.username, order.payment_sum_without_application_fee)
    subject = LISTING_RECEIVED_SELLER_TITLE % order.listing.title
    send_email(text, subject=subject, recipient=order.listing.user.email)


def listing_with_issue_investigation_opened_buyer(order):
    text = LISTING_WITH_ISSUE_INVESTIGATION_OPENED_TEXT % (order.user.username, BOLD_STRING % order.listing.title)
    subject = LISTING_WITH_ISSUE_INVESTIGATION_OPENED_TITLE % order.listing.title
    send_email(text, subject=subject, recipient=order.user.email)


def funds_received_seller(order):
    text = FUNDS_RECEIVED_SELLER_TEXT % (order.listing.user.username, BOLD_STRING % order.listing.title,
                                         order.payment_sum_without_application_fee)
    subject = FUNDS_RECEIVED_SELLER_TITLE % order.listing.title
    send_email(text, subject=subject, recipient=order.listing.user.email)


def refunds_issues_buyer(self):
    text = REFUND_ISSUES_BUYER_TEXT % (self.user.username, BOLD_STRING % self.listing.title,
                                       self.charge.payment_sum)
    subject = REFUND_ISSUES_BUYER_TITLE % self.listing.title
    send_email(text, subject=subject, recipient=self.user.email)


def transaction_canceled(email, username, title):
    text = TRANSACTION_CANCELED_TEXT % (username, BOLD_STRING % title)
    subject = TRANSACTION_CANCELED_TITLE % title
    send_email(text, subject=subject, recipient=email)


def investigation_resolved(email, username, title):
    text = INVESTIGATION_RESOLVED_TEXT % (username, BOLD_STRING % title)
    subject = INVESTIGATION_RESOLVED_TITLE % title
    send_email(text, subject=subject, recipient=email)


def send_warning_4_6_days_email(email, username, title):
    text = HAS_ITEM_RECEIVED_TEXT % username
    subject = HAS_ITEM_RECEIVED_TITLE % title
    send_email(text, subject=subject, recipient=email)


def user_withdrawal_requested_email(email, username, balance):
    text = WITHDRAWAL_REQUESTED_TEXT % (username, balance)
    subject = WITHDRAWAL_REQUESTED_TITLE
    send_email(text, subject=subject, recipient=email)


def user_withdrawal_completed_email(email, username, balance):
    text = WITHDRAWAL_COMPLETED_TEXT % (username, balance)
    subject = WITHDRAWAL_COMPLETED_TITLE
    send_email(text, subject=subject, recipient=email)