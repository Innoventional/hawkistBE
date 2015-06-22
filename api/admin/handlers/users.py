from api.admin.handlers.tags import AdminBaseHandler
from api.users.models import User
from base import paginate
from helpers import route

__author__ = 'ne_luboff'


@route('admin/users')
class AdminUsersHandler(AdminBaseHandler):
    allowed_methods = ('GET', )

    def read(self):
        users = self.session.query(User).order_by(User.id)

        page = self.get_arg('p', int, 1)
        page_size = self.get_arg('page_size', int, 100)

        paginator, tags = paginate(users, page, page_size)

        return self.render_string('admin/admin_users.html', users=users, paginator=paginator,
                                  menu_tab_active='tab_users')