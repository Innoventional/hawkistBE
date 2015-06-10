from email.mime.multipart import MIMEMultipart
import logging
import smtplib
from email.mime.text import MIMEText
from environment import env

__author__ = 'ne_luboff'


logger = logging.getLogger(__name__)


def send_email(text=None, subject=None, recipient=None, filename=None, recipients=None, html=None, template_name=None,
               from_email=None, **kwargs):
    msg = MIMEMultipart('alternative')
    if subject is None:
        subject = env['mail']['subject']

    if from_email is None:
        from_email = env['mail']['from']

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
    server.quit()