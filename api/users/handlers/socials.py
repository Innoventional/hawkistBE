import logging
from sqlalchemy import and_
from api.users.models import User
from base import ApiHandler, die
from helpers import route
from ui_messages.errors.users_errors.update_errors import UPDATE_USER_LINK_FB_NO_TOKEN, UPDATE_USER_FB_ALREADY_USED
from ui_messages.messages.custom_error_titles import UPDATE_USER_FB_ALREADY_USED_TITLE
from utility.facebook_api import get_facebook_user, get_facebook_photo, get_facebook_friends
from utility.user_utility import update_user_last_activity, check_user_suspension_status

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('user/socials')
class UserSocialHandler(ApiHandler):
    allowed_methods = ('PUT', 'GET')

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

        facebook_token = self.get_arg('facebook_token', str, None)

        if not facebook_token:
            return self.make_error('No fb token')

        facebook_response = get_facebook_friends(facebook_token)
        facebook_error, facebook_data = facebook_response['error'], facebook_response['data']
        if facebook_error:
            return self.make_error(facebook_error)

        friends = self.session.query(User).filter(and_(User.facebook_id.in_(facebook_data),
                                                       User.visible_in_find_friends == True))
        return self.success({'users': [{
            'id': u.id,
            'avatar': u.avatar,
            'username': u.username,
            'following': True if u in self.user.following else False
        } for u in friends]})

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

        logger.debug('REQUEST_OBJECT_USER_SOCIAL')
        logger.debug(self.request_object)

        facebook_token = ''

        if self.request_object:
            if 'facebook_token' in self.request_object:
                facebook_token = self.request_object['facebook_token']

        if not facebook_token:
            return self.make_error(UPDATE_USER_LINK_FB_NO_TOKEN)

        facebook_response = get_facebook_user(facebook_token)
        facebook_error, facebook_data = facebook_response['error'], facebook_response['data']
        if facebook_error:
            return self.make_error(facebook_error)
        if not facebook_data:
            return self.make_error('Something wrong! Try again later')
        facebook_id = facebook_data['id']

        # check is this facebook id available
        already_used = self.session.query(User).filter(and_(User.facebook_id == facebook_id,
                                                            User.id != self.user.id)).first()
        if already_used:
            return self.make_error(message=UPDATE_USER_FB_ALREADY_USED, title=UPDATE_USER_FB_ALREADY_USED_TITLE)

        self.user.facebook_id = facebook_id

        # if this user have not avatar picture get it from his facebook profile
        if not self.user.avatar:
            fb_avatar_response = get_facebook_photo(facebook_token)
            fb_avatar_error, fb_avatar_data = fb_avatar_response['error'], fb_avatar_response['data']
            if not fb_avatar_error:
                self.user.avatar = fb_avatar_data['avatar']
                self.user.thumbnail = fb_avatar_data['thumbnail']
            else:
                logger.debug(fb_avatar_error)
        self.session.commit()
        return self.success({'user': self.user.user_response})
