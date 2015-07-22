import logging
from api.admin.handlers.tags import AdminBaseHandler
from base import HttpRedirect
from helpers import route

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('admin/users/blocked')
class AdminBlockedUsersHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'DELETE')

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        blocked_users = self.session.execute('''
                SELECT * FROM user_blacklist;
            ''')

        return self.render_string('admin/users/admin_blocked_users.html', blocked_users=blocked_users,
                                  menu_tab_active='tab_users')
