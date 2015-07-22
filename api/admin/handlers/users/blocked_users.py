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

        # first get all info from flocked user table
        blocked_users = self.session.execute("""SELECT user_id as user_id,
                                                       blocked_user_id as b_user_id FROM user_blacklist;""")

        return self.render_string('admin/users/admin_blocked_users.html', blocked_users=blocked_users,
                                  menu_tab_active='tab_users')
