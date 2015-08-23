import logging
from api.users.models import User, SystemStatus
from base import ApiHandler, die
from helpers import route
from ui_messages.errors.followers_errors.followers_errors import FOLLOWING_NO_USER_TO_FOLLOW_ID, \
    FOLLOWING_NO_USER_TO_FOLLOW, FOLLOWING_ALREADY_FOLLOW_THIS_USER, FOLLOWING_TRY_FOLLOW_YOURSELF, \
    FOLLOWING_NO_USER_TO_UNFOLLOW_ID, FOLLOWING_TRY_UNFOLLOW_YOURSELF, FOLLOWING_ALREADY_UNFOLLOW_THIS_USER, \
    INVALID_USER_ID
from ui_messages.errors.users_errors.blocked_users_error import GET_BLOCKED_USER_FOLLOWERS
from ui_messages.errors.users_errors.suspended_users_errors import GET_SUSPENDED_USER_FOLLOWERS
from ui_messages.errors.users_errors.update_errors import NO_USER_WITH_ID
from utility.notifications import notification_new_follower
from utility.user_utility import update_user_last_activity, check_user_suspension_status

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('user/followers')
class FollowersHandler(ApiHandler):
    allowed_methods = ('GET', 'POST', 'DELETE')

    def read(self):

        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        # get is this get request for followers or following me people
        following = self.get_arg('following', bool, None)
        user_id = self.get_arg('user_id', None)
        user = None

        # get followers/following of another user
        if user_id:
            # first of all check is received user id int type
            try:
                user_id = int(user_id)
            except:
                return self.make_error(INVALID_USER_ID % user_id.upper())

            user = self.session.query(User).get(user_id)
            if not user:
                return self.make_error(NO_USER_WITH_ID % user_id)

            # check access to this user
            if self.user in user.blocked:
                return self.make_error(GET_BLOCKED_USER_FOLLOWERS % user.username.upper())

            # check is user active
            if user.system_status == SystemStatus.Suspended:
                return self.make_error(GET_SUSPENDED_USER_FOLLOWERS % user.username.upper())

        # get following people
        following_response = []
        if following:
            if user:
                f_users = user.following
                for u in f_users:
                    current_response = u.following_response
                    current_response['follow'] = u in self.user.following
                    following_response.append(current_response)
            else:
                f_users = self.user.following
                following_response = [u.following_response for u in f_users]
        # or people I follow
        else:
            if user:
                f_users = user.followers
                for u in f_users:
                    current_response = u.following_response
                    current_response['follow'] = u in self.user.following
                    following_response.append(current_response)
            else:
                f_users = self.user.followers
                following_response = [u.following_response for u in f_users]

        return self.success({
            'users': following_response
        })

    def create(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        logger.debug('REQUEST_OBJECT_FOLLOW_USER')
        logger.debug(self.request_object)

        user_to_follow_id = None

        # try get id for user to be followed by current user
        if self.request_object:
            user_to_follow_id = self.request_object['user_id']

        # if there is no user to follow id return an error
        if not user_to_follow_id:
            return self.make_error(FOLLOWING_NO_USER_TO_FOLLOW_ID)

        # maybe you try follow yourself
        if str(self.user.id) == str(user_to_follow_id):
            return self.make_error(FOLLOWING_TRY_FOLLOW_YOURSELF)

        # try get user to follow by id
        user_to_follow = self.session.query(User).get(user_to_follow_id)

        # if where is no user to follow in our db
        if not user_to_follow:
            return self.make_error(FOLLOWING_NO_USER_TO_FOLLOW % user_to_follow_id)

        # check access to user
        if self.user in user_to_follow.blocked:
            return self.make_error(GET_BLOCKED_USER_FOLLOWERS % user_to_follow.username.upper())

        # check is user active
        if user_to_follow.system_status == SystemStatus.Suspended:
            return self.make_error(GET_SUSPENDED_USER_FOLLOWERS % user_to_follow.username.upper())

        # check is you already follow this user
        if user_to_follow in self.user.following:
            return self.make_error(FOLLOWING_ALREADY_FOLLOW_THIS_USER % user_to_follow.username.upper())

        # else add this user to current user following
        self.user.following.append(user_to_follow)
        notification_new_follower(user_to_follow_id)
        self.session.commit()

        return self.success()

    def remove(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        user_to_unfollow_id = self.get_arg('user_id', int, None)

        # if there is no user to unfollow id return an error
        if not user_to_unfollow_id:
            return self.make_error(FOLLOWING_NO_USER_TO_UNFOLLOW_ID)

        # maybe you try unfollow yourself
        if str(self.user.id) == str(user_to_unfollow_id):
            return self.make_error(FOLLOWING_TRY_UNFOLLOW_YOURSELF)

        # try get user to unfollow by id
        user_to_unfollow = self.session.query(User).get(user_to_unfollow_id)

        # if where is no user to unfollow in our db
        if not user_to_unfollow:
            return self.make_error(FOLLOWING_NO_USER_TO_FOLLOW % user_to_unfollow_id)

        # check is you already unfollow this user
        if user_to_unfollow not in self.user.following:
            return self.make_error(FOLLOWING_ALREADY_UNFOLLOW_THIS_USER % user_to_unfollow.username.upper())

        # else remove this user from current user following
        self.user.following.remove(user_to_unfollow)
        self.session.commit()

        return self.success()