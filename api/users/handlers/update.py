import logging
import datetime
from sqlalchemy import and_, func, or_
from api.tags.models import Tag, Platform, Category, Subcategory
from api.users.models import User, UserTags, UserMetaTag, UserMetaTagType
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

        if not username:
            return self.make_error('Username is required')

        if not email:
            return self.make_error('Email is required')

        need_commit = False

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

            # save username in case if usernames not the same
            if self.user.username != username:
                self.user.username = username
                need_commit = True

        # EMAIL handler
        if email:
            email = str(email.encode('utf-8')).lower()
            # first validate email
            email_error = email_verification(email)
            if email_error:
                return self.make_error(email_error)

            if self.user.email != email:
                self.user.email = email
                # send email confirmation
                email_confirmation_sending(self, self.user, email)
                need_commit = True

        # about me handler
        if about_me:
            if self.user.info != about_me:
                self.user.info = about_me
                need_commit = True

        # avatar handler
        if self.request.files:
            img = self.request.files.values()[0][0]['body']
            thumbnail = make_thumbnail(img)

            try:
                image_url = upload_file('avatar-%d' % self.user.id, img, content_type='image/png')
                thumbnail_url = upload_file('thumbnail-%d' % self.user.id, thumbnail, content_type='image/png')
                self.user.avatar = image_url
                self.user.thumbnail = thumbnail_url
                need_commit = True
            except Exception, e:
                logger.debug(e)

        if need_commit:
            self.user.updated_at = datetime.datetime.utcnow()
            self.session.commit()

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

@route('user/metatags')
class UserMetaTagsHandler(ApiHandler):
    allowed_methods = ('PUT', 'DELETE')

    def update(self):

        if self.user is None:
            die(401)

        logger.debug('REQUEST_OBJECT_USER_ADD_METATAGS')
        logger.debug(self.request_object)

        metatag_ids = []

        if self.request_object:
            if 'tags' in self.request_object:
                metatag_ids = self.request_object['tags']

        if not metatag_ids:
            logger.debug('No tags to be added to user %s' % self.user)

        if metatag_ids:
            for metatag in metatag_ids:
                """
                every metatag which must be added to user for customization feeds consist of type (platform, category,
                subcategory) and metatag id
                """
                metatag_id = metatag['id']
                metatag_type = metatag['type']
                if not metatag_id:
                    return self.make_error('No metatag id')
                if not metatag_type:
                    return self.make_error('No metatag type')

                # does client side sent digits?
                try:
                    metatag_id = int(metatag_id)
                except ValueError:
                    return self.make_error('%s is not a number' % metatag_id)

                # 'cause we have 3 types check is received metatag type valid
                if metatag_type not in [0, 1, 2]:
                    return self.make_error('Invalid metatag type')

                # for go through every possible type
                if metatag_type == 0:
                    metatag_type = UserMetaTagType.Platform

                    # check is this platform exists
                    platform = self.session.query(Platform).filter(Platform.id == metatag_id).first()
                    if not platform:
                        return self.make_error('Platform which you try add does not exists. Update tag list')

                    # is this tag already exists in this user
                    already_exists = self.session.query(UserMetaTag).filter(and_(UserMetaTag.user_id == self.user.id,
                                                                                 UserMetaTag.metatag_type == metatag_type,
                                                                                 UserMetaTag.platform.id == platform.id)).first()
                    if already_exists:
                        return self.make_error('You already added platform %s to your feeds' % (platform.title.upper()))

                    # else create new user metatag
                    user_platform_tag = UserMetaTag()
                    user_platform_tag.user = self.user
                    self.session.add(user_metatag)
                    self.session.commit()
                elif metatag_type == 1:
                    metatag_type = UserMetaTagType.Category
                elif metatag_type == 2:
                    metatag_type = UserMetaTagType.Subcategory

                return

                # try get this metatag from platform / category / subcategory
                platform_metatag = self.session.query(Platform).filter(Platform.id == metatag_id)
                category_metatag = self.session.query(Category).filter(Category.id == metatag_id)
                subcategory_metatag = self.session.query(Subcategory).filter(Subcategory.id == metatag_id)
                if not platform_metatag and not category_metatag and not subcategory_metatag:
                    return self.make_error('No metatag with id %s' % metatag_id)

                # check for platform
                if platform_metatag:
                    already_exists = self.session.query(UserMetaTag).filter(and_(UserMetaTag.user_id == self.user.id,
                                                                                 UserMetaTag.platform_id == metatag_id)).first()
                    if already_exists:
                        return self.make_error('You already added tag %s to your feeds' % already_exists.platform.title.upper())

                # check for category
                if category_metatag:
                    already_exists = self.session.query(UserMetaTag).filter(and_(UserMetaTag.user_id == self.user.id,
                                                                                 UserMetaTag.category_id == metatag_id)).first()
                    if already_exists:
                        return self.make_error('You already added tag %s to your feeds' % already_exists.category.title.upper())

                # check for subcategory
                if subcategory_metatag:
                    already_exists = self.session.query(UserMetaTag).filter(and_(UserMetaTag.user_id == self.user.id,
                                                                                 UserMetaTag.subcategory_id == metatag_id)).first()
                    if already_exists:
                        return self.make_error('You already added tag %s to your feeds' % already_exists.subcategory.title.upper())

                user_metatag = UserMetaTag()
                user_metatag.user = self.user
                if platform_metatag:
                    user_metatag.platform_id = metatag_id
                elif category_metatag:
                    user_metatag.category_id = metatag_id
                elif subcategory_metatag:
                    user_metatag.subcategory_id = metatag_id
                self.session.add(user_metatag)
                self.session.commit()


        return self.success({'user': self.user.user_response})

    def remove(self):

        if self.user is None:
            die(401)

        logger.debug('REQUEST_OBJECT_USER_DELETE_METATAGS')
        logger.debug(self.request_object)

        metatag_ids = []

        if self.request_object:
            if 'tags' in self.request_object:
                metatag_ids = self.request_object['tags']

        if not metatag_ids:
            logger.debug('No tags to be deleted from user %s' % self.user)

        if metatag_ids:
            # matatag to be added for user consists of metatag type and id
            for metatag in metatag_ids:
                metatag_id = metatag['id']
                metatag_type = metatag['type']
                if not metatag_id:
                    return self.make_error('No metatag id')
                if not metatag_type:
                    return self.make_error('No metatag type')
                # tag value to int
                try:
                    metatag_id = int(metatag_id)

                    # Get user metatag pair by metatag id
                    user_metatag = self.session.query(UserMetaTag).filter(and_(UserMetaTag.user_id == self.user.id,
                                                                               or_(UserMetaTag.platform_id == metatag_id,
                                                                                   UserMetaTag.category_id == metatag_id,
                                                                                   UserMetaTag.subcategory_id == metatag_id))).first()
                    if not user_metatag:
                        logger('User %s havent metatag %s' % (self.user.id, metatag_id))
                    else:
                        self.session.delete(user_metatag)
                        self.session.commit()
                except ValueError:
                    logger.debug('%s is not a number' % metatag_id)

        return self.success({'user': self.user.user_response})
