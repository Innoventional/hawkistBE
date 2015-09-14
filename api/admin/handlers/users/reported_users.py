import logging
import datetime
from api.admin.handlers.login import AdminBaseHandler
from api.users.models import User, SystemStatus
from api.users.reported_users.models import UserReportingReasons, ReportedUsers
from base import HttpRedirect
from helpers import route

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

        reported_users = self.session.query(ReportedUsers).order_by(ReportedUsers.id)

        blocked_users_count = 0
        blocked_users_count_query = self.session.execute("""SELECT count(*) as ca FROM user_blacklist;""")
        for b in blocked_users_count_query:
            blocked_users_count = b.ca

        suspended_users_count = self.session.query(User).filter(User.system_status == SystemStatus.Suspended).count()

        return self.render_string('admin/users/admin_reported_users.html', reported_users=reported_users,
                                  menu_tab_active='tab_users', blocked_users_count=blocked_users_count,
                                  UserReportingReasons=UserReportingReasons, timedelta=datetime.timedelta,
                                  suspended_users_count=suspended_users_count)