import logging
from api.admin.handlers.login import AdminBaseHandler
from api.users.models import User, SystemStatus, UserType
from api.users.reported_users.models import ReportedUsers
from base import HttpRedirect
from helpers import route

__author__ = 'ne_luboff'


logger = logging.getLogger(__name__)


@route('admin/users/suspended')
class AdminSuspendedUsersHandler(AdminBaseHandler):
    allowed_methods = ('GET', )

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        users = self.session.query(User).filter(User.system_status == SystemStatus.Suspended).order_by(User.id)

        q = self.get_argument('q')

        if q:
            users = users.filter(User.username.ilike(u'%{0}%'.format(q)))

        blocked_users_count = 0
        blocked_users_count_query = self.session.execute("""SELECT count(*) as ca FROM user_blacklist;""")
        for b in blocked_users_count_query:
            blocked_users_count = b.ca

        suspended_users_count = self.session.query(User).filter(User.system_status == SystemStatus.Suspended).count()
        reported_users_count = self.session.query(ReportedUsers).count()

        return self.render_string('admin/users/admin_suspended_users.html', users=users, menu_tab_active='tab_users',
                                  SystemStatus=SystemStatus, UserType=UserType, current_user=self.user, q=q,
                                  blocked_users_count=blocked_users_count, suspended_users_count=suspended_users_count,
                                  reported_users_count=reported_users_count)