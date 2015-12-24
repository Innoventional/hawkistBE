import logging
import datetime
from random import choice
import string
from urllib2 import urlopen
from sqlalchemy import or_, and_
from api.users.models import User, SystemStatus, UserType
from base import ApiHandler, die, OpenApiHandler
from helpers import route
from ui_messages.errors.users_errors.login_errors import SIGN_UP_EMPTY_AUTHORIZATION_DATA, \
    LOG_IN_EMPTY_AUTHORIZATION_DATA, LOG_IN_USER_NOT_FOUND, LOG_IN_INCORRECT_PIN
from ui_messages.messages.custom_error_titles import PHONE_VERIFICATION_INVALID_FORMAT_TITLE, \
    LOG_IN_EMPTY_AUTHORIZATION_DATA_TITLE, LOG_IN_USER_NOT_FOUND_TITLE, LOG_IN_INCORRECT_PIN_TITLE, \
    UPDATE_USER_INFO_EMAIL_ALREADY_USED_TITLE
from ui_messages.messages.sms import SIGN_UP_WELCOME_SMS, REQUEST_NEW_PIN_SMS
from utility.amazon import upload_file
from utility.facebook_api import get_facebook_user, get_facebook_photo
from utility.format_verification import phone_verification, sms_limit_check
from utility.send_email import email_confirmation_sending
from utility.twilio_api import send_sms
from utility.user_utility import update_user_last_activity, check_user_suspension_status, check_email_uniqueness

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


class UserLoginNotFoundException(Exception):
    pass


@route('users')
class UserLoginHandler(ApiHandler):
    allowed_methods = ('POST', 'GET', 'PUT')

    def create(self):
        logger.debug("REQUEST_OBJECT_USER_LOGIN")
        logger.debug(self.request_object)
        user = None
        phone = ''
        facebook_token = ''

        if self.request_object:
            if 'phone' in self.request_object:
                phone = self.request_object['phone']
            if 'facebook_token' in self.request_object:
                facebook_token = self.request_object['facebook_token']

        if not phone and not facebook_token:
            return self.make_error(SIGN_UP_EMPTY_AUTHORIZATION_DATA)

        # for phone number authorization
        if phone:
            # we must to know is this new user to choose sms which will be sent to him
            new_user = False
            # first of all delete + symbol
            phone = str(phone)
            phone = phone.replace('+', '')
            # first verify number
            phone_error = phone_verification(phone)
            if phone_error:
                return self.make_error(message=phone_error, title=PHONE_VERIFICATION_INVALID_FORMAT_TITLE)

            # try get existing user
            user = self.session.query(User).filter(User.phone == phone).first()
            if not user:
                logger.debug('Create new user (phone registration)')
                user = User()
                user.created_at = datetime.datetime.utcnow()
                user.phone = phone
                user.first_login = True
                user.system_status = SystemStatus.Active
                user.user_type = UserType.Standard
                user.sent_pins_count = 0
                user.last_activity = datetime.datetime.utcnow()
                self.session.flush(user)
                new_user = True

            # check user status
            suspension_error = check_user_suspension_status(user)
            if suspension_error:
                logger.debug(suspension_error)
                return suspension_error
            # check user ability to send one more sms
            reach_sms_limit = sms_limit_check(self)
            if reach_sms_limit:
                return self.make_error(reach_sms_limit)

            # generate pin code
            confirm_code = ''.join(choice(string.digits) for _ in xrange(4))
            if new_user:
                message_body = SIGN_UP_WELCOME_SMS % confirm_code
            else:
                message_body = REQUEST_NEW_PIN_SMS % confirm_code

            # and send it to user
            error = send_sms(phone, message_body)
            if error:
                return self.make_error(message=error, title=PHONE_VERIFICATION_INVALID_FORMAT_TITLE)

            user.pin = confirm_code
            user.last_pin_sending = datetime.datetime.utcnow()
            user.sent_pins_count += 1
            user.updated_at = datetime.datetime.utcnow()
            self.session.add(user)
            self.session.commit()
        elif facebook_token:
            facebook_response = get_facebook_user(facebook_token)
            facebook_error, facebook_data = facebook_response['error'], facebook_response['data']
            if facebook_error:
                return self.make_error(facebook_error)
            facebook_id = facebook_data.get('id', None)
            if not facebook_id:
                return self.make_error('Something wrong! Try again later')

            # try get existing fb user
            user = self.session.query(User).filter(User.facebook_id == facebook_id).first()

            if not user:
                logger.debug('Create new user (fb registration)')

                # first check email
                facebook_email = facebook_data.get('email', None)
                email_uniqueness_error = check_email_uniqueness(self, facebook_email)
                if email_uniqueness_error:
                    return self.make_error(message=email_uniqueness_error,
                                           title=UPDATE_USER_INFO_EMAIL_ALREADY_USED_TITLE)

                user = User()
                user.created_at = datetime.datetime.utcnow()
                user.facebook_id = facebook_id
                user.first_login = True
                user.system_status = SystemStatus.Active
                user.user_type = UserType.Standard
                user.last_activity = datetime.datetime.utcnow()
                self.session.add(user)
                self.session.commit()

                #  add avatar
                fb_avatar_response = get_facebook_photo(facebook_token)
                fb_avatar_error, fb_avatar_data = fb_avatar_response['error'], fb_avatar_response['data']
                if not fb_avatar_error:
                    # must upload photo to amazon
                    try:
                        avatar_url = upload_file('avatar-%d-production' % user.id,
                                                 urlopen(fb_avatar_data['avatar']).read(), content_type='image/png')
                        thumbnail_url = upload_file('thumbnail-%d-production' % user.id,
                                                    urlopen(fb_avatar_data['thumbnail']).read(),
                                                    content_type='image/png')
                        user.avatar = avatar_url
                        user.thumbnail = thumbnail_url
                        self.session.commit()
                    except Exception, e:
                        logger.debug(e)
                else:
                    logger.debug(fb_avatar_error)

                # getting email
                # facebook_email = facebook_data.get('email', None)
                # if facebook_email:
                #     user.email = facebook_email
                #     email_confirmation_sending(self, user, facebook_email)
                # else:
                #     logger.debug('No email address in fb response')


                facebook_name = facebook_data.get('username', None)
                if facebook_name:
                    # replaced all whitespaces with underscore symbol
                    user.username = facebook_name.replace(" ", "_")

                user.email = facebook_email
                email_confirmation_sending(self, user, facebook_email)

                self.session.commit()
            # else:
                # if user.email and user.username:
                #     user.first_login = False
                # self.session.commit()

            # check user status
            suspension_error = check_user_suspension_status(user)
            if suspension_error:
                logger.debug(suspension_error)
                return suspension_error
            self.user = user
            self.session.commit()

        return self.success({'user': user.user_response})

    def read(self):

        if self.user is None:
            die(401)

        # we must to know user who do this request
        logger.debug(self.user)

        # update user last active
        update_user_last_activity(self)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        # NOTE! Suspended users exclude from all users query
        # users who added current user to black list too
        blocked_me_users_id = [u.id for u in self.user.blocked_me]
        qs = self.session.query(User).filter(and_(User.id != self.user.id,
                                                  User.system_status == SystemStatus.Active,
                                                  ~User.id.in_(blocked_me_users_id))).order_by(User.id)

        q = self.get_argument('q')

        if q:
            qs = qs.filter(or_(User.email.ilike(u'%{0}%'.format(q)),
                               User.username.ilike(u'%{0}%'.format(q)))).order_by(User.id)

        response = {
            'status': 0,
            'users': [user.user_response for user in qs]
        }
        logger.debug(response)
        return response

    def update(self):
        logger.debug("REQUEST_OBJECT_USER_LOGIN_CONFIRM_CODE")
        logger.debug(self.request_object)
        user = None
        phone = ''
        pin = ''

        if self.request_object:
            if 'phone' in self.request_object:
                phone = self.request_object['phone']
            if 'pin' in self.request_object:
                pin = str(self.request_object['pin'])

        if not phone or not pin:
            return self.make_error(message=LOG_IN_EMPTY_AUTHORIZATION_DATA, title=LOG_IN_EMPTY_AUTHORIZATION_DATA_TITLE)

        # first of all delete + symbol
        phone = str(phone)
        phone = phone.replace('+', '')
        phone_error = phone_verification(phone)
        if phone_error:
            return self.make_error(message=phone_error, title=PHONE_VERIFICATION_INVALID_FORMAT_TITLE)

        user = self.session.query(User).filter(User.phone == phone).first()

        if not user:
            return self.make_error(message=LOG_IN_USER_NOT_FOUND % phone, title=LOG_IN_USER_NOT_FOUND_TITLE)

        logger.debug(user)

        # check user status
        suspension_error = check_user_suspension_status(user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        if user.pin != pin:
            return self.make_error(message=LOG_IN_INCORRECT_PIN % pin, title=LOG_IN_INCORRECT_PIN_TITLE)

        # if user.username and user.email:
        #     user.first_login = False
        self.user = user
        self.session.commit()
        return self.success({'user': self.user.user_response})


@route('user/logout')
class LogoutHandler(OpenApiHandler):
    allowed_methods = ('PUT', )

    def update(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        # delete apns_token
        if self.user.apns_token:
            self.user.apns_token = None

        self.user = None

        self.session.commit()

        return self.success()