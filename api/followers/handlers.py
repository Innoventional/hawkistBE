import logging
from api.users.models import User
from base import ApiHandler, die
from helpers import route
from ui_messages.errors.followers_errors.followers_errors import FOLLOWING_NO_USER_TO_FOLLOW_ID, \
    FOLLOWING_NO_USER_TO_FOLLOW, FOLLOWING_ALREADY_FOLLOW_THIS_USER, FOLLOWING_TRY_FOLLOW_YOURSELF, \
    FOLLOWING_NO_USER_TO_UNFOLLOW_ID, FOLLOWING_TRY_UNFOLLOW_YOURSELF, FOLLOWING_ALREADY_UNFOLLOW_THIS_USER

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('user/followers')
class FollowersHandler(ApiHandler):
    allowed_methods = ('GET', 'POST', 'DELETE')

    def read(self):

        if self.user is None:
            die(401)

        # get is this get request for followers or following me people
        following = self.get_arg('following', bool, None)

        # get following people
        if following:
            print 'here'
            f_users = self.user.following
        # or people I follow
        else:
            f_users = self.user.followers

        return self.success({
            'users': [u.following_response for u in f_users]
        })

    def create(self):
        if self.user is None:
            die(401)

        user_to_follow_id = None

        # try get id for user to be followed by current user
        if self.request_object:
            user_to_follow_id = self.request_object['user_id']

        # if there is no user to follow id return an error
        if not user_to_follow_id:
            return self.make_error(FOLLOWING_NO_USER_TO_FOLLOW_ID)

        # maybe you try follow yourself
        if self.user.id == user_to_follow_id:
            return self.make_error(FOLLOWING_TRY_FOLLOW_YOURSELF)

        # try get user to follow by id
        user_to_follow = self.session.query(User).get(user_to_follow_id)

        # if where is no user to follow in our db
        if not user_to_follow:
            return self.make_error(FOLLOWING_NO_USER_TO_FOLLOW % user_to_follow_id)

        # check is you already follow this user
        if user_to_follow in self.user.following:
            return self.make_error(FOLLOWING_ALREADY_FOLLOW_THIS_USER % user_to_follow.username.upper())

        # else add this user to current user following
        self.user.following.append(user_to_follow)
        self.session.commit()

        return self.success()

    def remove(self):
        if self.user is None:
            die(401)

        user_to_unfollow_id = self.get_arg('user_id', int, None)

        # if there is no user to unfollow id return an error
        if not user_to_unfollow_id:
            return self.make_error(FOLLOWING_NO_USER_TO_UNFOLLOW_ID)

        # maybe you try unfollow yourself
        if self.user.id == user_to_unfollow_id:
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