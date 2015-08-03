import logging
from api.users.models import User
from base import ApiHandler, die
from helpers import route
from ui_messages.errors.users_errors.blocked_users_error import BLOCK_USER_NO_USER_ID, BLOCK_USER_TRY_BLOCK_YOURSELF, \
    BLOCK_USER_ALREADY_BLOCKED_USER, BLOCK_USER_NO_USER_TO_UNBLOCK_ID, BLOCK_USER_TRY_UNBLOCK_YOURSELF, \
    BLOCK_USER_ALREADY_UNBLOCKED_USER
from ui_messages.errors.users_errors.update_errors import NO_USER_WITH_ID
from utility.user_utility import update_user_last_activity, check_user_suspension_status

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('user/blocking')
class BlockingUsersHandler(ApiHandler):
    allowed_methods = ('POST', 'DELETE', )

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

        logger.debug('REQUEST_OBJECT_BLOCK_USER')
        logger.debug(self.request_object)

        user_to_block_id = None

        # try get id for user to be blocked by current user
        if self.request_object:
            user_to_block_id = self.request_object['user_id']

        # if there is no user to follow id return an error
        if not user_to_block_id:
            return self.make_error(BLOCK_USER_NO_USER_ID)

        # maybe you try block yourself
        if str(self.user.id) == str(user_to_block_id):
            return self.make_error(BLOCK_USER_TRY_BLOCK_YOURSELF)

        # try get user to block by id
        user_to_block = self.session.query(User).get(user_to_block_id)

        # if where is no user to block in our db
        if not user_to_block:
            return self.make_error(NO_USER_WITH_ID % user_to_block_id)

        # check is you already follow this user
        if user_to_block in self.user.blocked:
            return self.make_error(BLOCK_USER_ALREADY_BLOCKED_USER % user_to_block.username.upper())

        # else add this user to current user blocked
        self.user.blocked.append(user_to_block)
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

        user_to_unblock_id = self.get_arg('user_id', int, None)

        # if there is no user to unblock id return an error
        if not user_to_unblock_id:
            return self.make_error(BLOCK_USER_NO_USER_TO_UNBLOCK_ID)

        # maybe you try unblock yourself
        if str(self.user.id) == str(user_to_unblock_id):
            return self.make_error(BLOCK_USER_TRY_UNBLOCK_YOURSELF)

        # try get user to unblock by id
        user_to_unblock = self.session.query(User).get(user_to_unblock_id)

        # if where is no user to unblock in our db
        if not user_to_unblock:
            return self.make_error(NO_USER_WITH_ID % user_to_unblock_id)

        # check is you already unblock this user
        if user_to_unblock not in self.user.blocked:
            return self.make_error(BLOCK_USER_ALREADY_UNBLOCKED_USER % user_to_unblock.username.upper())

        # else remove this user from current user blocked users
        self.user.blocked.remove
        self.session.commit()

        return self.success()
