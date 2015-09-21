import logging
import datetime
from sqlalchemy import and_, func
from api.tags.models import Platform, Category, Subcategory
from api.users.models import User, UserMetaTag, UserMetaTagType
from base import ApiHandler, die, USER_ID, OpenApiHandler
from helpers import route
from ui_messages.errors.users_errors.blocked_users_error import GET_BLOCKED_USER
from ui_messages.errors.users_errors.update_errors import NO_USER_WITH_ID,UPDATE_USER_INFO_USERNAME_ALREADY_USED,\
    INVALID_CONFIRM_EMAIL_LINK, UPDATE_USER_TAGS_TAG_DOES_NOT_EXISTS, UPDATE_USER_TAGS_TAG_ALREADY_ADDED, \
    UPDATE_USER_TAGS_NO_TAG_ID, \
    UPDATE_USER_TAGS_NO_TAG_TYPE, UPDATE_USER_TAGS_INVALID_TAG_ID, UPDATE_USER_TAGS_INVALID_TAG_TYPE, \
    UPDATE_USER_TAGS_NO_EXISTING_USER_TAG, UPDATE_USER_INFO_MISSING_USERNAME_OR_EMAIL
from ui_messages.messages.custom_error_titles import USERNAME_VERIFICATION_INVALID_FORMAT_TITLE, \
    CREATE_LISTING_EMPTY_FIELDS_TITLE, UPDATE_USER_INFO_USERNAME_ALREADY_USED_TITLE, \
    UPDATE_USER_INFO_EMAIL_ALREADY_USED_TITLE
from ui_messages.messages.email import CONFIRM_SUCCESS_EMAIL_LETTER_SUBJECT, CONFIRM_SUCCESS_EMAIL_LETTER_TEXT
from utility.amazon import upload_file
from utility.format_verification import username_verification, email_verification
from utility.image.processor import make_thumbnail
from utility.notifications import update_notification_user_username, update_notification_user_avatar
from utility.send_email import email_confirmation_sending, send_email
from utility.user_utility import update_user_last_activity, check_user_suspension_status, check_email_uniqueness
from utility.zendesk_api import zendesk_create_jwt

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('user')
class UserHandler(ApiHandler):
    allowed_methods = ('GET', 'POST')

    def read(self):

        if self.user is None:
            die(401)

        logger.debug(self.user)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

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
                return self.make_error(message=GET_BLOCKED_USER % user.username.encode('utf-8').upper(),
                                       status=3)

            # else we must show following details
            user_response = user.user_response

            # does this user follow you
            user_response['follow'] = True if user in self.user.followers else False

            # do you follow this user
            user_response['following'] = True if user in self.user.following else False
            user_response['blocked'] = True if user in self.user.blocked else False
            user_response['blocked_me'] = True if self.user in user.blocked else False
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

        logger.debug(self.user)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

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

        # check email and username
        no_email_username_error = []
        if not username:
            no_email_username_error.append('username')

        if not email:
            no_email_username_error.append('email')

        if no_email_username_error:
            empty_fields = ', '.join(no_email_username_error)
            return self.make_error(message=UPDATE_USER_INFO_MISSING_USERNAME_OR_EMAIL % empty_fields,
                                   title=CREATE_LISTING_EMPTY_FIELDS_TITLE % empty_fields.capitalize())

        need_commit = False

        # USERNAME handler
        if username:
            username = str(username.encode('utf-8'))
            # first validate username
            username_error = username_verification(username)
            if username_error:
                return self.make_error(message=username_error, title=USERNAME_VERIFICATION_INVALID_FORMAT_TITLE)

            already_used = self.session.query(User).filter(and_(User.id != self.user.id,
                                                                func.lower(User.username) == username.lower())).first()
            if already_used:
                return self.make_error(message=UPDATE_USER_INFO_USERNAME_ALREADY_USED % username,
                                       title=UPDATE_USER_INFO_USERNAME_ALREADY_USED_TITLE)

            # save username in case if usernames not the same
            if self.user.username != username:
                self.user.username = username
                need_commit = True
                update_notification_user_username(self, self.user)

        # EMAIL handler
        if email:
            email = str(email.encode('utf-8')).lower()
            # first validate email
            email_error = email_verification(email)
            if email_error:
                return self.make_error(message=email_error, title=USERNAME_VERIFICATION_INVALID_FORMAT_TITLE)

            if self.user.email != email:
                email_uniqueness_error = check_email_uniqueness(self, email)
                if email_uniqueness_error:
                    return self.make_error(message=email_uniqueness_error,
                                           title=UPDATE_USER_INFO_EMAIL_ALREADY_USED_TITLE)
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
                image_url = upload_file('avatar-%d-production' % self.user.id, img, content_type='image/png')
                thumbnail_url = upload_file('thumbnail-%d-production' % self.user.id, thumbnail,
                                            content_type='image/png')
                self.user.avatar = image_url
                self.user.thumbnail = thumbnail_url
                need_commit = True
                update_notification_user_avatar(self, self.user)
            except Exception, e:
                logger.debug(e)

        if need_commit:
            self.user.updated_at = datetime.datetime.utcnow()
            self.session.commit()

        if self.user.email and self.user.username:
            self.user.first_login = False
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

        # send message about success
        text = CONFIRM_SUCCESS_EMAIL_LETTER_TEXT % user.username
        subject = CONFIRM_SUCCESS_EMAIL_LETTER_SUBJECT
        send_email(text, subject=subject, recipient=user.email)
        return self.render_string('ui/welcome.html', menu_tab_active='')


@route('user/metatags')
class UserMetaTagsHandler(ApiHandler):
    allowed_methods = ('GET', 'POST', 'PUT')

    def read(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        # TODO old method which get only not included user tags (2015-09-12)
        # first we must get users metatags
        # existing_user_tags_id = [metatag.platform_id for metatag in self.session.query(UserMetaTag).filter(and_(UserMetaTag.user_id == self.user.id,
        #                                                                                                         UserMetaTag.metatag_type == UserMetaTagType.Platform))]
        # tags_to_be_added = self.session.query(Platform).filter(~Platform.id.in_(existing_user_tags_id)).order_by(Platform.id)
        #
        # return self.success(
        #     {
        #         "tags": [t.response for t in tags_to_be_added]
        #     }
        # )

        included_user_platforms = [user_tag.platform_id for user_tag in self.user.user_metatags]
        tag_response = []
        platforms = self.session.query(Platform).order_by(Platform.id)
        for p in platforms:
            current_response = p.response
            current_response['available'] = True if p.id not in included_user_platforms else False
            tag_response.append(current_response)
        return self.success({
            'tags': tag_response
        })

    def create(self):

        if self.user is None:
            die(401)

        logger.debug(self.user)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

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
                if str(metatag_type) not in ['0', '1', '2']:
                    return self.make_error(UPDATE_USER_TAGS_INVALID_TAG_TYPE)

                # for go through every possible type
                if str(metatag_type) == '0':
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

    def update(self):

        if self.user is None:
            die(401)

        logger.debug(self.user)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

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
                if str(metatag_type) not in ['0', '1', '2']:
                    return self.make_error(UPDATE_USER_TAGS_INVALID_TAG_TYPE)

                if str(metatag_type) == '0':
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

@route('delete_anthony_tags')
class DeleteAnthonyTagsHandler(OpenApiHandler):
    allowed_methods = ('GET', )

    def read(self):
        anthony_tags = self.session.query(UserMetaTag).filter(UserMetaTag.user_id == 77)
        if anthony_tags.count() == 0:
            return 'No tags to be deleted'

        tag_response = ''
        for tag in anthony_tags:
            tag_response += tag.platform.title + ' '
            self.session.delete(tag)
            self.session.commit()

        return 'Deleted %s' % tag_response


@route('user/apns_token')
class UserAPNSTokenHandler(ApiHandler):
    allowed_methods = ('PUT',)

    def update(self):

        if self.user is None:
            die(401)

        logger.debug(self.user)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        logger.debug('REQUEST_OBJECT_USER_APNS_TOKEN')
        logger.debug(self.request_object)

        apns_token = ''

        if self.request_object:
            if 'apns_token' in self.request_object:
                apns_token = str(self.request_object['apns_token'])

        if not apns_token:
            return self.make_error('Anton, attention! No apns token in request')

        # set apns_token to user
        # first check has any user this token
        need_commit = False

        users_with_this_token = self.session.query(User).filter(and_(User.apns_token == apns_token,
                                                                     User.id != self.user.id))
        for u in users_with_this_token:
            u.apns_token = None
            u.updated_at = datetime.datetime.utcnow()
            need_commit = True

        # update token if current user has another
        if self.user.apns_token != apns_token:
            self.user.apns_token = apns_token
            need_commit = True

        if need_commit:
            self.user.updated_at = datetime.datetime.utcnow()
            self.session.commit()

        return self.success()


@route('user/jwt')
class UserJWTHandler(ApiHandler):
    allowed_methods = ('GET',)

    def read(self):

        if self.user is None:
            die(401)

        logger.debug(self.user)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        jwt_response = zendesk_create_jwt(self.user.id, self.user.username, self.user.email)

        return self.success({'jwt': jwt_response['payload_encoded']})