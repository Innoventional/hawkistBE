import logging
import datetime
from api.admin.handlers.login import AdminBaseHandler
from api.users.models import User
from api.users.reported_users.models import UserReportingReasons
from base import HttpRedirect
from helpers import route
from ui_messages.errors.admin_errors.admin_blocked_users_error import ADMIN_NO_BLOCKER_OR_NO_BLOCKED_USER_ID
from ui_messages.errors.users_errors.blocked_users_error import BLOCK_USER_ALREADY_UNBLOCKED_USER

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('admin/users/reported')
class AdminReportedUsersHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'DELETE')

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)
        # first get all info from blocked user table
        sql_request = """SELECT user_reportlist.user_id as reporter_id,
                         user_reportlist.reported_user_id as reported_id,
                         user_reportlist.created_at as created_at,
                         user_reportlist.reason as reason,
                         (SELECT users.username FROM users where users.id = user_reportlist.user_id) as reporter_username,
                         (SELECT users.username FROM users where users.id = user_reportlist.reported_user_id) as reported_username
                         FROM user_reportlist INNER JOIN users
                         ON user_reportlist.user_id=users.id;"""
        reported_users = self.session.execute(sql_request)

        reported_users_count = 0
        reported_users_count_query = self.session.execute("""SELECT count(*) as ca FROM user_reportlist;""")
        for b in reported_users_count_query:
            reported_users_count = b.ca

        return self.render_string('admin/users/admin_reported_users.html', reported_users=reported_users,
                                  reported_users_count=reported_users_count, menu_tab_active='tab_users',
                                  UserReportingReasons=UserReportingReasons, timedelta=datetime.timedelta)

    # def remove(self):
    #     if not self.user:
    #         return HttpRedirect('/api/admin/login')
    #
    #     logger.debug(self.user)
    #
    #     # first get blocker and blocked users id from request parameters
    #     blocker_id = self.get_arg('blocker_id', int, None)
    #     blocked_id = self.get_arg('blocked_id', int, None)
    #
    #     if not blocker_id or not blocked_id:
    #         return self.make_error(ADMIN_NO_BLOCKER_OR_NO_BLOCKED_USER_ID)
    #
    #     blocker = self.session.query(User).get(blocker_id)
    #     if not blocker:
    #         return self.make_error('Something wrong. Try again later')
    #
    #     blocked = self.session.query(User).get(blocked_id)
    #     if not blocked:
    #         return self.make_error('Something wrong. Try again later')
    #
    #     if blocked not in blocker.blocked:
    #         return self.make_error(BLOCK_USER_ALREADY_UNBLOCKED_USER % blocked.username.upper())
    #
    #     blocker.blocked.remove(blocked)
    #     self.session.commit()
    #     return self.success()