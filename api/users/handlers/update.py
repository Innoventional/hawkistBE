import logging
from sqlalchemy import and_
from api.users.models import User
from base import ApiHandler, die
from helpers import route
from utility.amazon import upload_file
from utility.format_verification import username_verification, email_verification
from utility.image.processor import make_thumbnail

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)

@route('user')
class UserHandler(ApiHandler):
    allowed_methods = ('GET', 'PUT')

    def read(self):

        if self.user is None:
            die(401)

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