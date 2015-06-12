import logging
from random import choice
import string
from sqlalchemy import and_, Enum
from api.users.models import User, UserTags
from base import ApiHandler, die, USER_ID
from environment import env
from helpers import route, encrypt_password
from utility.amazon import upload_file
from utility.facebook_api import get_facebook_user
from utility.format_verification import username_verification, email_verification
from utility.image.processor import make_thumbnail
from utility.send_email import send_email

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


class Tags(Enum):
    PS = 0
    PC = 1
    XBox = 2

    @classmethod
    def tostring(cls, val):
        for k, v in vars(cls).iteritems():
            if v == val:
                return k


@route('user')
class UserHandler(ApiHandler):
    allowed_methods = ('GET', 'PUT')

    def read(self):

        if self.user is None:
            die(401)

        # update cookies
        self.set_secure_cookie(USER_ID, str(self.user.id), expires_days=30)

        user_id = self.get_arg('id', int)
        if user_id:
            user = self.session.query(User).get(user_id)
            if not user:
                return self.make_error('No user with id %s' % user_id)
            return self.success({'user': user.user_response})
        else:
            logger.debug(self.get_secure_cookie('user-id'))
            if self.user is None:
                die(401)
            else:
                return self.success({'user': self.user.user_response})

    def update(self):

        if self.user is None:
            die(401)

        logger.debug('REQUEST_OBJECT_USER_UPDATE')
        logger.debug(self.request_object)

        username = ''
        email = ''
        about_me = ''

        if 'username' in self.request_object:
            username = str(self.request_object['username'].encode('utf-8')).lower()
        if 'email' in self.request_object:
            email = str(self.request_object['email']).lower()
        if 'about_me' in self.request_object:
            about_me = self.request_object['about_me']

        if not username and not email and not about_me and not self.request.files:
            logger.debug('Nothing to be updated')

        # USERNAME handler
        if username:
            # first validate username
            username_error = username_verification(username)
            if username_error:
                return self.make_error(username_error)

            already_used = self.session.query(User).filter(and_(User.id != self.user.id,
                                                                User.username == username)).first()
            if already_used:
                return self.make_error("Sorry, username '%s' already used by another user" % username)

            self.user.username = username

        # EMAIL handler
        if email:
            # first validate email
            email_error = email_verification(email)
            if email_error:
                return self.make_error(email_error)

            already_used = self.session.query(User).filter(and_(User.id != self.user.id,
                                                                User.email == email)).first()
            if already_used:
                return self.make_error("Sorry, email address '%s' already used by another user" % email)

            self.user.email = email

            # send email confirmation
            email_salt = encrypt_password(password=email, salt=env['password_salt'])
            self.user.email_salt = email_salt

            text = 'Welcome to Hawkist!\nTo confirm your email address use the link bellow:\n' + env['server_address'] \
                   + '/api/user/confirm_email/' + email_salt
            subject = 'Email confirmation'
            send_email(text, subject=subject, recipient=self.user.email)

        # about me handler
        if about_me:
            self.user.info = about_me

        self.session.commit()

        # avatar handler
        if self.request.files:
            img = self.request.files.values()[0][0]['body']
            thumbnail = make_thumbnail(img)

            try:
                image_url = upload_file('avatar-%d' % self.user.id, img, content_type='image/jpeg')
                thumbnail_url = upload_file('thumbnail-%d' % self.user.id, thumbnail, content_type='image/jpeg')
                self.user.photo = image_url
                self.user.thumbnail = thumbnail_url
                self.session.commit()
            except Exception, e:
                logger.debug(e)

        return self.success({'user': self.user.user_response})


@route('user/confirm_email/(.*)')
class UserEmailVerificationHandler(ApiHandler):
    allowed_methods = ('GET', )

    def read(self, email_salt):

        if self.user is None:
            die(401)

        if self.user.email_salt != email_salt:
            return self.make_error('Invalid confirmation link. Try again')
        self.user.email_status = True
        self.session.commit()

        return self.success({'user': self.user.user_response})


@route('user/socials')
class UserSocialHandler(ApiHandler):
    allowed_methods = ('PUT', )

    def update(self):

        if self.user is None:
            die(401)

        logger.debug('REQUEST_OBJECT_USER_SOCIAL')
        logger.debug(self.request_object)

        facebook_token = ''

        if 'facebook_token' in self.request_object:
            facebook_token = self.request_object['facebook_token']

        if not facebook_token:
            return self.make_error('No facebook token')

        facebook_response = get_facebook_user(facebook_token)
        facebook_error, facebook_id = facebook_response['error'], facebook_response['data']
        if facebook_error:
            return self.make_error(facebook_error)
        if not facebook_id:
            return self.make_error('Something wrong! Try again later')

        # check is this facebook id available
        already_used = self.session.query(User).filter(and_(User.facebook_id == facebook_id,
                                                            User.id != self.user.id)).first()
        if already_used:
            return self.make_error('This facebook account is already used by another user.')

        self.user.facebook_id = facebook_id
        self.session.commit()
        return self.success({'user': self.user.user_response})


@route('user/tags')
class UserTagsHandler(ApiHandler):
    allowed_methods = ('PUT', )

    def update(self):

        if self.user is None:
            die(401)

        logger.debug('REQUEST_OBJECT_USER_TAGS')
        logger.debug(self.request_object)

        tags = []

        if 'tags' in self.request_object:
            tags = self.request_object['tags']

        if not tags:
            logger.debug('No tags to be added to user %s' % self.user)

        if tags:
            for tag in tags:
                # tag value to int
                try:
                    tag = int(tag)
                    tag_name = Tags.tostring(tag)
                    if tag_name:
                        user_tag = UserTags()
                        user_tag.user = self.user
                        user_tag.tag_id = tag
                        self.session.add(user_tag)
                        self.session.commit()
                except ValueError:
                    logger.debug('%s is not a number' % tag)

        return self.success({'user': self.user.user_response})
