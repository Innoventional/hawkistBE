import logging
from api.admin.handlers.login import AdminBaseHandler
from api.users.models import User, SystemStatus, UserType
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

        return self.render_string('admin/users/admin_suspended_users.html', users=users, menu_tab_active='tab_users',
                                  SystemStatus=SystemStatus, UserType=UserType, current_user=self.user, q=q)