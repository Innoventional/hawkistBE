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

        # SELECT Orders.OrderID, Customers.CustomerName, Orders.OrderDate
# FROM Orders
# INNER JOIN Customers
# ON Orders.CustomerID=Customers.CustomerID;

        # first get all info from flocked user table
        sql_request = """SELECT user_blacklist.user_id as user_id,
                         user_blacklist.blocked_user_id as b_user_id, users.username as u_u FROM user_blacklist INNER JOIN users
                         ON user_blacklist.user_id=users.id OR user_blacklist.blocked_user_id=users.id;"""
        blocked_users = self.session.execute(sql_request)

        return self.render_string('admin/users/admin_blocked_users.html', blocked_users=blocked_users,
                                  menu_tab_active='tab_users')
