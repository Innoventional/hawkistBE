import logging
import datetime
from api.admin.handlers.login import AdminBaseHandler
from api.users.models import User, SystemStatus
from api.users.reported_users.models import ReportedUsers
from base import HttpRedirect
from helpers import route
from ui_messages.errors.admin_errors.admin_blocked_users_error import ADMIN_NO_BLOCKER_OR_NO_BLOCKED_USER_ID
from ui_messages.errors.users_errors.blocked_users_error import BLOCK_USER_ALREADY_UNBLOCKED_USER

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('admin/users/blocked')
class AdminBlockedUsersHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'DELETE')

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)
        # first get all info from blocked user table
        sql_request = """SELECT user_blacklist.user_id as blocker_id,
                         user_blacklist.blocked_user_id as blocked_id,
                         user_blacklist.created_at as created_at,
                         (SELECT users.username FROM users where users.id = user_blacklist.user_id) as blocker_username,
                         (SELECT users.username FROM users where users.id = user_blacklist.blocked_user_id) as blocked_username
                         FROM user_blacklist INNER JOIN users
                         ON user_blacklist.user_id=users.id;"""
        blocked_users = self.session.execute(sql_request)

        blocked_users_count = 0
        blocked_users_count_query = self.session.execute("""SELECT count(*) as ca FROM user_blacklist;""")
        for b in blocked_users_count_query:
            blocked_users_count = b.ca

        suspended_users_count = self.session.query(User).filter(User.system_status == SystemStatus.Suspended).count()
        reported_users_count = self.session.query(ReportedUsers).count()
        return self.render_string('admin/users/admin_blocked_users.html', blocked_users=blocked_users,
                                  blocked_users_count=blocked_users_count, menu_tab_active='tab_users',
                                  timedelta=datetime.timedelta, suspended_users_count=suspended_users_count,
                                  reported_users_count=reported_users_count)

    def remove(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        # first get blocker and blocked users id from request parameters
        blocker_id = self.get_arg('blocker_id', int, None)
        blocked_id = self.get_arg('blocked_id', int, None)

        if not blocker_id or not blocked_id:
            return self.make_error(ADMIN_NO_BLOCKER_OR_NO_BLOCKED_USER_ID)

        blocker = self.session.query(User).get(blocker_id)
        if not blocker:
            return self.make_error('Something wrong. Try again later')

        blocked = self.session.query(User).get(blocked_id)
        if not blocked:
            return self.make_error('Something wrong. Try again later')

        if blocked not in blocker.blocked:
            return self.make_error(BLOCK_USER_ALREADY_UNBLOCKED_USER % blocked.username.upper())

        blocker.blocked.remove(blocked)
        self.session.commit()
        return self.success()