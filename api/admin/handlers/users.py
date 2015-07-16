import logging
from random import choice
import string
import datetime
from sqlalchemy import and_, func
from api.admin.handlers.tags import AdminBaseHandler
from api.users.models import User, SystemStatus, UserType
from base import paginate, HttpRedirect
from environment import env
from helpers import route, encrypt_password
from ui_messages.errors.admin_errors.admin_users_errors import ADMIN_UPDATE_USER_HAS_NOT_EMAIL, \
    ADMIN_UPDATE_USER_NOT_CONFIRM_EMAIL
from ui_messages.errors.users_errors.update_errors import UPDATE_USER_INFO_USERNAME_ALREADY_USED, \
    UPDATE_USER_PHONE_ALREADY_USED
from ui_messages.messages.admin_tool import ADMIN_USERTYPE_CHANGED_SUCCESS
from ui_messages.messages.custom_error_titles import PHONE_VERIFICATION_INVALID_FORMAT_TITLE
from ui_messages.messages.email import ADMIN_BACK_USER_TO_STANDARD_USERTYPE_LETTER_TEXT, ADMIN_CHANGE_USERTYPE_LETTER_TEXT, \
    ADMIN_CHANGE_USERTYPE_LETTER_SUBJECT, ADMIN_PHONE_NUMBER_CHANGED_LETTER_TEXT, \
    ADMIN_PHONE_NUMBER_CHANGED_LETTER_SUBJECT
from ui_messages.messages.sms import UPDATE_USER_PHONE_NUMBER_SMS
from utility.format_verification import username_verification, email_verification, phone_verification
from utility.send_email import send_email, email_confirmation_sending
from utility.twilio_api import send_sms

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('admin/users')
class AdminUsersHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        users = self.session.query(User).order_by(User.id)

        # pagination function
        # first get require page number
        # if not require page number set it to 1 and return first page
        page = self.get_arg('p', int, 1)
        # get require page size
        # if not require page size set it to 100 and return 100 items
        page_size = self.get_arg('page_size', int, 100)
        # properly pagination handler
        paginator, tags = paginate(users, page, page_size)

        return self.render_string('admin/admin_users.html', users=users, paginator=paginator,
                                  menu_tab_active='tab_users', SystemStatus=SystemStatus, UserType=UserType,
                                  current_user=self.user)

    def create(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        user_id = self.get_arg('user_id')
        new_user_type = int(self.get_arg('user_type_id'))

        # check is user exists
        user = self.session.query(User).filter(User.id == user_id).first()
        if not user:
            return self.make_error('Something wrong. Try again later')

        # has chosen user email in his profile
        if not user.email:
            return self.make_error(ADMIN_UPDATE_USER_HAS_NOT_EMAIL)

        # did chosen user confirm his email address
        if not user.email_status:
            return self.make_error(ADMIN_UPDATE_USER_NOT_CONFIRM_EMAIL)

        # check is usertype changed
        if user.user_type != new_user_type:
            # text for email message
            text = ''
            # if user transferred to standard user group
            if new_user_type == 3:
                text = ADMIN_BACK_USER_TO_STANDARD_USERTYPE_LETTER_TEXT % UserType.tostring(user.user_type)
            # an another cases
            else:
                # generate password to log in in admin tool
                # select all chars - lower and upper
                chars = string.ascii_letters
                # generate 8 random chars
                password = ''.join(choice(chars) for _ in xrange(8))
                # then randomly choose digits number (min - 1, max - 4)
                number_count = choice([i for i in range(1, 4)])
                while number_count != 0:
                    # randomly get digit position
                    gap_position = choice([i for i in xrange(8)])
                    # randomly get digit
                    number = choice([i for i in xrange(10)])
                    # set it randomly digit on randomly position in chars password
                    password = password[:gap_position] + str(number) + password[gap_position:]
                    number_count -= 1

                # encrypt password and set it to user
                encrypted_pass = encrypt_password(password=password, salt=env['password_salt'])
                user.password = encrypted_pass
                # email text
                text = ADMIN_CHANGE_USERTYPE_LETTER_TEXT % \
                       (UserType.tostring(new_user_type), env['server_address'] + '/api/admin/login', password)
            # change usertype
            user.user_type = new_user_type
            # send email
            subject = ADMIN_CHANGE_USERTYPE_LETTER_SUBJECT
            send_email(text, subject=subject, recipient=user.email)
            # commit changes
            self.session.commit()
        return self.success({'message': ADMIN_USERTYPE_CHANGED_SUCCESS % UserType.tostring(new_user_type)})

    def update(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        user_id = self.get_arg('user_id')
        action = self.get_arg('action')

        # get user to be changed
        user = self.session.query(User).filter(User.id == user_id).first()
        if not user:
            return self.make_error('Something wrong. Try again later')

        need_commit = False

        # depending on the action do next
        if action == 'suspend':
            user.system_status = 1
            need_commit = True

        elif action == 'unsuspend':
            user.system_status = 0
            need_commit = True

        elif action == 'edit':
            username = self.get_arg('username')
            email = self.get_arg('email')
            phone = self.get_arg('phone')

            # step-by-step
            # username
            if user.username != username and username:
                # username verification
                # username can consist of string, digits, dash symbols and dots
                username = str(username.encode('utf-8'))
                username_error = username_verification(username)
                if username_error:
                    return self.make_error(username_error)

                # check is username available
                already_used = self.session.query(User).filter(and_(User.id != user.id,
                                                                    func.lower(User.username) == username.lower())).first()
                if already_used:
                    return self.make_error(UPDATE_USER_INFO_USERNAME_ALREADY_USED % username)
                user.username = username
                need_commit = True

            # email
            if user.email != email and email:
                email = str(email.encode('utf-8')).lower()
                # validate email
                email_error = email_verification(email)
                if email_error:
                    return self.make_error(email_error)

                user.email = email
                # change email confirmation status
                user.email_status = False
                # send email confirmation
                email_confirmation_sending(self, user, email)
                need_commit = True

            # phone
            if user.phone != phone and phone:
                phone = str(phone)
                phone = phone.replace('+', '')
                # verify number
                phone_error = phone_verification(phone)
                if phone_error:
                    return self.make_error(phone_error)

                already_used = self.session.query(User).filter(and_(User.id != user.id,
                                                                    User.phone == phone)).first()
                if already_used:
                    return self.make_error(UPDATE_USER_PHONE_ALREADY_USED % phone)

                # send message to email
                if user.email:
                    text = ADMIN_PHONE_NUMBER_CHANGED_LETTER_TEXT
                    subject = ADMIN_PHONE_NUMBER_CHANGED_LETTER_SUBJECT
                    send_email(text, subject=subject, recipient=user.email)

                # generate pin code
                confirm_code = ''.join(choice(string.digits) for _ in xrange(4))
                message_body = UPDATE_USER_PHONE_NUMBER_SMS % confirm_code

                # and send it to user
                error = send_sms(phone, message_body)
                if error:
                    response = {
                        'status': 2,
                        'message': error,
                        'title': PHONE_VERIFICATION_INVALID_FORMAT_TITLE
                    }
                    logger.debug(response)
                    return response

                user.phone = phone
                user.pin = confirm_code
                user.last_pin_sending = datetime.datetime.utcnow()
                if user.sent_pins_count:
                    user.sent_pins_count += 1
                else:
                    user.sent_pins_count = 0
                need_commit = True

        if need_commit:
            user.updated_at = datetime.datetime.utcnow()
            self.session.commit()

        return self.success()

    def remove(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        user_id = self.get_arg('user_id')
        user = self.session.query(User).filter(User.id == user_id).first()
        if not user:
            return self.make_error('Something wrong. Try again later')
        self.session.delete(user)
        self.session.commit()
        return self.success()
