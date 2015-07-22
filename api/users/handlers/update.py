import logging
import datetime
from sqlalchemy import and_, func, or_
from api.tags.models import Tag, Platform, Category, Subcategory
from api.users.models import User, UserTags, UserMetaTag, UserMetaTagType
from base import ApiHandler, die, USER_ID, OpenApiHandler
from helpers import route
from ui_messages.errors.users_errors.blocked_users_error import GET_BLOCKED_USER
from ui_messages.errors.users_errors.update_errors import NO_USER_WITH_ID, UPDATE_USER_INFO_NO_USERNAME, \
    UPDATE_USER_INFO_NO_EMAIL, UPDATE_USER_INFO_USERNAME_ALREADY_USED, INVALID_CONFIRM_EMAIL_LINK, \
    UPDATE_USER_LINK_FB_NO_TOKEN, UPDATE_USER_FB_ALREADY_USED, UPDATE_USER_TAGS_TAG_DOES_NOT_EXISTS, \
    UPDATE_USER_TAGS_TAG_ALREADY_ADDED, UPDATE_USER_TAGS_NO_TAG_ID, UPDATE_USER_TAGS_NO_TAG_TYPE, \
    UPDATE_USER_TAGS_INVALID_TAG_ID, UPDATE_USER_TAGS_INVALID_TAG_TYPE, UPDATE_USER_TAGS_NO_EXISTING_USER_TAG
from utility.amazon import upload_file
from utility.facebook_api import get_facebook_user
from utility.format_verification import username_verification, email_verification
from utility.image.processor import make_thumbnail
from utility.send_email import email_confirmation_sending
from utility.user_utility import update_user_last_activity, check_user_suspension_status

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('user')
class UserHandler(ApiHandler):
    allowed_methods = ('GET', 'POST')

    def read(self):

        if self.user is None:
            die(401)

        update_user_last_activity(self)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        # update cookies
        self.set_secure_cookie(USER_ID, str(self.user.id), expires_days=30)

        # try get user id from address row to know do you want see your own profile or profile of another user
        user_id = self.get_arg('id', int)
        # another user profile
        if user_id:

            # try get another user
            user = self.session.query(User).get(user_id)

            # if there is no user with this id - return an error
            if not user:
                return self.make_error(NO_USER_WITH_ID % user_id)

            # check has current user access to getting user profile
            if self.user in user.blocked:
                return self.make_error(GET_BLOCKED_USER % user.username.upper())

            # else we must show following details
            user_response = user.user_response

            # does this user follow you
            user_response['follow'] = True if user in self.user.followers else False

            # do you follow this user
            user_response['following'] = True if user in self.user.following else False
            user_response['blocked'] = True if user in self.user.blocked else False
            return self.success({'user': user_response})
        # your own profile
        else:
            logger.debug(self.get_secure_cookie('user-id'))
            if self.user is None:
                die(401)
            else:
                return self.success({'user': self.user.user_response})

    def create(self):

        if self.user is None:
            die(401)

        update_user_last_activity(self)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

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
            return self.make_error(UPDATE_USER_INFO_NO_USERNAME)

        if not email:
            return self.make_error(UPDATE_USER_INFO_NO_EMAIL)

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
                return self.make_error(UPDATE_USER_INFO_USERNAME_ALREADY_USED % username)

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
                self.user.email_status = False
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
            return self.render_string('ui/error.html', message=INVALID_CONFIRM_EMAIL_LINK)

        user.email_status = True
        self.session.commit()
        return self.render_string('ui/welcome.html', menu_tab_active='')


@route('user/socials')
class UserSocialHandler(ApiHandler):
    allowed_methods = ('PUT', )

    def update(self):

        if self.user is None:
            die(401)

        update_user_last_activity(self)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        logger.debug('REQUEST_OBJECT_USER_SOCIAL')
        logger.debug(self.request_object)

        facebook_token = ''

        if self.request_object:
            if 'facebook_token' in self.request_object:
                facebook_token = self.request_object['facebook_token']

        if not facebook_token:
            return self.make_error(UPDATE_USER_LINK_FB_NO_TOKEN)

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
            return self.make_error(UPDATE_USER_FB_ALREADY_USED)

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

        update_user_last_activity(self)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

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
                metatag_id = metatag.get('id', None)
                metatag_type = metatag.get('type', None)

                if not metatag_id:
                    return self.make_error(UPDATE_USER_TAGS_NO_TAG_ID)
                if len(str(metatag_type)) == 0:
                    return self.make_error(UPDATE_USER_TAGS_NO_TAG_TYPE)

                # does client side sent digits?
                try:
                    metatag_id = int(metatag_id)
                except ValueError:
                    return self.make_error(UPDATE_USER_TAGS_INVALID_TAG_ID % metatag_id)

                # 'cause we have 3 types check is received metatag type valid
                if metatag_type not in [0, 1, 2]:
                    return self.make_error(UPDATE_USER_TAGS_INVALID_TAG_TYPE)

                # for go through every possible type
                if metatag_type == 0:
                    metatag_type = UserMetaTagType.Platform

                    # check is this platform exists
                    platform = self.session.query(Platform).filter(Platform.id == metatag_id).first()
                    if not platform:
                        return self.make_error(UPDATE_USER_TAGS_TAG_DOES_NOT_EXISTS % 'Platform')

                    # is this tag already exists in this user
                    already_exists = self.session.query(UserMetaTag).filter(and_(UserMetaTag.user_id == self.user.id,
                                                                                 UserMetaTag.metatag_type == metatag_type,
                                                                                 UserMetaTag.platform_id == platform.id)).first()
                    if already_exists:
                        return self.make_error(UPDATE_USER_TAGS_TAG_ALREADY_ADDED % ('platform',
                                                                                     platform.title.upper()))

                    # else create new user metatag
                    user_platform_tag = UserMetaTag()
                    user_platform_tag.user = self.user
                    user_platform_tag.metatag_type = metatag_type
                    user_platform_tag.platform = platform
                    self.session.add(user_platform_tag)
                    self.session.commit()
                elif metatag_type == 1:
                    metatag_type = UserMetaTagType.Category

                    # check is this category exists
                    category = self.session.query(Category).filter(Category.id == metatag_id).first()
                    if not category:
                        return self.make_error(UPDATE_USER_TAGS_TAG_DOES_NOT_EXISTS % 'Category')

                    # is this category tag already added to this user feeds
                    already_exists = self.session.query(UserMetaTag).filter(and_(UserMetaTag.user_id == self.user.id,
                                                                                 UserMetaTag.metatag_type == metatag_type,
                                                                                 UserMetaTag.category_id == category.id)).first()
                    if already_exists:
                        return self.make_error(UPDATE_USER_TAGS_TAG_ALREADY_ADDED % ('category',
                                                                                     '%s (%s)'
                                                                                     % (category.title.upper(),
                                                                                        category.platform.title.upper())))

                    # else create new user metatag
                    user_category_tag = UserMetaTag()
                    user_category_tag.user = self.user
                    user_category_tag.metatag_type = metatag_type
                    user_category_tag.category = category
                    self.session.add(user_category_tag)
                    self.session.commit()
                elif metatag_type == 2:
                    metatag_type = UserMetaTagType.Subcategory

                    # check is this subcategory exists
                    subcategory = self.session.query(Subcategory).filter(Subcategory.id == metatag_id).first()
                    if not subcategory:
                        return self.make_error(UPDATE_USER_TAGS_TAG_DOES_NOT_EXISTS % 'Subcategory')

                    # is this subcategory tag already added to this user feeds
                    already_exists = self.session.query(UserMetaTag).filter(and_(UserMetaTag.user_id == self.user.id,
                                                                                 UserMetaTag.metatag_type == metatag_type,
                                                                                 UserMetaTag.subcategory_id == subcategory.id)).first()
                    if already_exists:
                        return self.make_error(UPDATE_USER_TAGS_TAG_ALREADY_ADDED % ('subcategory',
                                                                                     '%s (%s > %s)'
                                                                                     % (subcategory.title.upper(),
                                                                                        subcategory.category.platform.title.upper(),
                                                                                        subcategory.category.title.upper())))

                    # else create new user metatag
                    user_subcategory_tag = UserMetaTag()
                    user_subcategory_tag.user = self.user
                    user_subcategory_tag.metatag_type = metatag_type
                    user_subcategory_tag.subcategory = subcategory
                    self.session.add(user_subcategory_tag)
                    self.session.commit()

        return self.success({'user': self.user.user_response})

    def remove(self):

        if self.user is None:
            die(401)

        update_user_last_activity(self)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        logger.debug('REQUEST_OBJECT_USER_DELETE_METATAGS')
        logger.debug(self.request_object)

        metatag_ids = []

        if self.request_object:
            if 'tags' in self.request_object:
                metatag_ids = self.request_object['tags']

        if not metatag_ids:
            logger.debug('No tags to be deleted from user %s' % self.user)

        if metatag_ids:
            for metatag in metatag_ids:
                metatag_id = metatag.get('id', None)
                metatag_type = metatag.get('type', None)

                if not metatag_id:
                    return self.make_error(UPDATE_USER_TAGS_NO_TAG_ID)
                if len(str(metatag_type)) == 0:
                    return self.make_error(UPDATE_USER_TAGS_NO_TAG_TYPE)

                # does client side sent digits?
                try:
                    metatag_id = int(metatag_id)
                except ValueError:
                    return self.make_error(UPDATE_USER_TAGS_INVALID_TAG_ID % metatag_id)

                # 'cause we have 3 types check is received metatag type valid
                if metatag_type not in [0, 1, 2]:
                    return self.make_error(UPDATE_USER_TAGS_INVALID_TAG_TYPE)

                if metatag_type == 0:
                    metatag_type = UserMetaTagType.Platform

                    platform = self.session.query(Platform).filter(Platform.id == metatag_id).first()
                    if not platform:
                        return self.make_error(UPDATE_USER_TAGS_TAG_DOES_NOT_EXISTS % 'Platform')

                    user_platform_metatag = self.session.query(UserMetaTag).filter(and_(UserMetaTag.user_id == self.user.id,
                                                                                        UserMetaTag.metatag_type == metatag_type,
                                                                                        UserMetaTag.platform_id == platform.id)).first()
                    if not user_platform_metatag:
                        return self.make_error(UPDATE_USER_TAGS_NO_EXISTING_USER_TAG % ('platform',
                                                                                        platform.title.upper()))

                    self.session.delete(user_platform_metatag)
                    self.session.commit()
                elif metatag_type == 1:
                    metatag_type = UserMetaTagType.Category

                    category = self.session.query(Category).filter(Category.id == metatag_id).first()
                    if not category:
                        return self.make_error(UPDATE_USER_TAGS_TAG_DOES_NOT_EXISTS % 'Category')

                    user_category_metatag = self.session.query(UserMetaTag).filter(and_(UserMetaTag.user_id == self.user.id,
                                                                                        UserMetaTag.metatag_type == metatag_type,
                                                                                        UserMetaTag.category_id == category.id)).first()
                    if not user_category_metatag:
                        return self.make_error(UPDATE_USER_TAGS_NO_EXISTING_USER_TAG % ('category',
                                                                                        '%s (%s)'
                                                                                        % (category.title.upper(),
                                                                                           category.platform.title.upper())))

                    self.session.delete(user_category_metatag)
                    self.session.commit()
                elif metatag_type == 2:
                    metatag_type = UserMetaTagType.Subcategory

                    subcategory = self.session.query(Subcategory).filter(Subcategory.id == metatag_id).first()
                    if not subcategory:
                        return self.make_error(UPDATE_USER_TAGS_TAG_DOES_NOT_EXISTS % 'Subcategory')

                    user_subcategory_metatag = self.session.query(UserMetaTag).filter(and_(UserMetaTag.user_id == self.user.id,
                                                                                           UserMetaTag.metatag_type == metatag_type,
                                                                                           UserMetaTag.subcategory_id == subcategory.id)).first()
                    if not user_subcategory_metatag:
                        return self.make_error(UPDATE_USER_TAGS_NO_EXISTING_USER_TAG % ('subcategory',
                                                                                        '%s (%s > %s)'
                                                                                        % (subcategory.title.upper(),
                                                                                           subcategory.category.platform.title.upper(),
                                                                                           subcategory.category.title.upper())))

                    self.session.delete(user_subcategory_metatag)
                    self.session.commit()

        return self.success({'user': self.user.user_response})
