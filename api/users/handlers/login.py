import logging
import datetime
from random import choice
import string
from sqlalchemy import and_, or_
from api.users.models import User, SystemStatus, UserType
from base import ApiHandler, die, OpenApiHandler
from helpers import route
from utility.facebook_api import get_facebook_user, get_facebook_photo
from utility.format_verification import phone_verification, sms_limit_check
from utility.send_email import email_confirmation_sending
from utility.twilio_api import send_sms

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
            return self.make_error('Empty authorization data')

        # for phone number authorization
        if phone:
            # first of all delete + symbol
            phone = str(phone)
            phone = phone.replace('+', '')
            # first verify number
            phone_error = phone_verification(phone)
            if phone_error:
                return self.make_error(phone_error)

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
                self.session.add(user)
            else:
                user.first_login = False
                self.session.commit()

            # check user avability to send one more sms
            reach_sms_limit = sms_limit_check(self)
            if reach_sms_limit:
                return self.make_error(reach_sms_limit)

            # generate pin code
            confirm_code = ''.join(choice(string.digits) for _ in xrange(4))
            message_body = 'Welcome to Hawkist! Use this code to login:\n%s' % confirm_code

            # and send it to user
            error = send_sms(phone, message_body)
            if error:
                return self.make_error(error)

            user.pin = confirm_code
            user.last_pin_sending = datetime.datetime.utcnow()
            user.sent_pins_count += 1
            user.updated_at = datetime.datetime.utcnow()
            # self.session.add(user)
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
                user = User()
                user.created_at = datetime.datetime.utcnow()
                user.facebook_id = facebook_id
                user.first_login = True
                user.system_status = SystemStatus.Active
                user.user_type = UserType.Standard
                self.session.add(user)
                self.session.commit()

                #  add avatar
                fb_avatar_response = get_facebook_photo(facebook_token)
                fb_avatar_error, fb_avatar_data = fb_avatar_response['error'], fb_avatar_response['data']
                if not fb_avatar_error:
                    user.avatar = fb_avatar_data['avatar']
                    user.thumbnail = fb_avatar_data['thumbnail']
                    # self.session.commit()
                else:
                    logger.debug(fb_avatar_error)

                # getting email
                facebook_email = facebook_data.get('email', None)
                if facebook_email:
                    user.email = facebook_email
                    # self.session.commit()
                    email_confirmation_sending(self, user, facebook_email)
                else:
                    logger.debug('No email address in fb response')

                facebook_name = facebook_data.get('username', None)
                if facebook_name:
                    user.username = facebook_name
                self.session.commit()
            else:
                user.first_login = False
                self.session.commit()

            self.user = user
            self.session.commit()

        return self.success({'user': user.user_response})

    def read(self):

        if self.user is None:
            die(401)

        qs = self.session.query(User).filter(User.id != self.user.id).order_by(User.id)

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
            # return self.make_error('You must input phone and pin')
            return self.make_error('You must input a mobile number and a pin to sign in.')

        # first of all delete + symbol
        phone = str(phone)
        phone = phone.replace('+', '')

        user = self.session.query(User).filter(User.phone == phone).first()

        if not user:
            # return self.make_error('No user with phone number %s. Please Sign up' % phone)
            return self.make_error('There is no user with mobile number %s. Please check the mobile number or sign up.'
                                   % phone)

        if user.pin != pin:
            # return self.make_error('Wrong pin(%s). Try again enter this pin or request a new one' % pin)
            return self.make_error('The pin %s is incorrect. Please try again or request a new pin.' % pin)

        self.user = user
        self.session.commit()
        return self.success({'user': self.user.user_response})


@route('user/logout')
class LogoutHandler(OpenApiHandler):
    allowed_methods = ('PUT', )

    def update(self):
        if self.user is None:
            die(401)

        self.user = None
        self.session.commit()

        return self.success()