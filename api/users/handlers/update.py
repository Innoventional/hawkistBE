import logging
from sqlalchemy import and_, func
from api.tags.models import Tag
from api.users.models import User, UserTags
from base import ApiHandler, die, USER_ID, OpenApiHandler
from helpers import route
from utility.amazon import upload_file
from utility.facebook_api import get_facebook_user
from utility.format_verification import username_verification, email_verification
from utility.image.processor import make_thumbnail
from utility.send_email import email_confirmation_sending

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('user')
class UserHandler(ApiHandler):
    allowed_methods = ('GET', 'POST')

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

    def create(self):

        if self.user is None:
            die(401)

        username = ''
        email = ''
        about_me = ''

        if self.request_object:
            if 'username' in self.request_object:
                username = self.request_object['username']
            if 'email' in self.request_object:
                email = self.request_object['email']
            if 'about_me' in self.request_object:
                about_me = self.request_object['about_me']
        else:
            username = self.get_argument('username', default=None)
            email = self.get_argument('email', default=None)
            about_me = self.get_argument('about_me', default=None)

        if not username and not email and not about_me and not self.request.files:
            logger.debug('Nothing to be updated')

        logger.debug('REQUEST_OBJECT_USER_UPDATE')
        logger.debug('username %s' % username)
        logger.debug('email %s' % email)
        logger.debug('about_me %s' % about_me)

        # USERNAME handler
        if username:
            username = str(username.encode('utf-8'))
            # first validate username
            username_error = username_verification(username)
            if username_error:
                return self.make_error(username_error)

            already_used = self.session.query(User).filter(and_(User.id != self.user.id,
                                                                func.lower(User.username) == username.lower())).first()
            if already_used:
                return self.make_error("Sorry, username '%s' already used by another user" % username)

            self.user.username = username

        # EMAIL handler
        if email:
            email = str(email.encode('utf-8')).lower()
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
            email_confirmation_sending(self, self.user, email)

        # about me handler
        if about_me:
            self.user.info = about_me

        self.session.commit()

        # avatar handler
        if self.request.files:
            img = self.request.files.values()[0][0]['body']
            thumbnail = make_thumbnail(img)

            try:
                image_url = upload_file('avatar-%d' % self.user.id, img, content_type='image/png')
                thumbnail_url = upload_file('thumbnail-%d' % self.user.id, thumbnail, content_type='image/png')
                self.user.avatar = image_url
                self.user.thumbnail = thumbnail_url
                self.session.commit()
            except Exception, e:
                logger.debug(e)

        return self.success({'user': self.user.user_response})


@route('user/confirm_email/(.*)')
class UserEmailVerificationHandler(OpenApiHandler):
    allowed_methods = ('GET', )

    def read(self, email_salt):

        # get user by email_salt
        user = self.session.query(User).filter(User.email_salt == email_salt).first()
        if not user:
            return self.render_string('ui/error.html', message='Invalid confirmation link. Try again later')

        user.email_status = True
        self.session.commit()
        return self.render_string('ui/welcome.html', menu_tab_active='')


@route('user/socials')
class UserSocialHandler(ApiHandler):
    allowed_methods = ('PUT', )

    def update(self):

        if self.user is None:
            die(401)

        logger.debug('REQUEST_OBJECT_USER_SOCIAL')
        logger.debug(self.request_object)

        facebook_token = ''

        if self.request_object:
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
    allowed_methods = ('PUT', 'DELETE')

    def update(self):

        if self.user is None:
            die(401)

        logger.debug('REQUEST_OBJECT_USER_ADD_TAGS')
        logger.debug(self.request_object)

        tag_ids = []

        if self.request_object:
            if 'tags' in self.request_object:
                tag_ids = self.request_object['tags']

        if not tag_ids:
            logger.debug('No tags to be added to user %s' % self.user)

        if tag_ids:
            for tag_id in tag_ids:
                # tag value to int
                try:
                    tag_id = int(tag_id)
                    tag_item = self.session.query(Tag).filter(Tag.id == tag_id)
                    if not tag_item:
                        return self.make_error('No tag with id %s' % tag_id)
                    # check is this tag already added
                    already_exists = self.session.query(UserTags).filter(and_(UserTags.tag_id == tag_id,
                                                                              UserTags.user_id == self.user.id)).first()
                    if already_exists:
                        return self.make_error('You already added tag %s to your feeds' % already_exists.tag.name)
                    user_tag = UserTags()
                    user_tag.user = self.user
                    user_tag.tag_id = tag_id
                    self.session.add(user_tag)
                    self.session.commit()
                except ValueError:
                    logger.debug('%s is not a number' % tag_id)

        return self.success({'user': self.user.user_response})

    def remove(self):

        if self.user is None:
            die(401)

        logger.debug('REQUEST_OBJECT_USER_DELETE_TAGS')
        logger.debug(self.request_object)

        tag_ids = []

        if self.request_object:
            if 'tags' in self.request_object:
                tag_ids = self.request_object['tags']

        if not tag_ids:
            logger.debug('No tags to be deleted from user %s' % self.user)

        if tag_ids:
            for tag_id in tag_ids:
                # tag value to int
                try:
                    tag_id = int(tag_id)
                    tag_item = self.session.query(Tag).filter(Tag.id == tag_id).first()
                    if not tag_item:
                        return self.make_error('No tag with id %s' % tag_id)
                    # check is this tag already added
                    tag_exists = self.session.query(UserTags).filter(and_(UserTags.tag_id == tag_id,
                                                                          UserTags.user_id == self.user.id)).first()
                    if not tag_exists:
                        return self.make_error("You haven\'t tag %s into your feeds" % tag_item.name)
                    self.session.delete(tag_exists)
                    self.session.commit()
                except ValueError:
                    logger.debug('%s is not a number' % tag_id)

        return self.success({'user': self.user.user_response})
