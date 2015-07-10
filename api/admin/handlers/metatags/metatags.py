from api.admin.handlers.tags import AdminBaseHandler
from api.tags.models import Platform
from base import HttpRedirect
from helpers import route

__author__ = 'ne_luboff'


@route('/admin/metatags')
class AdminMetatagHandler(AdminBaseHandler):
    allowed_methods = ('GET', )

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        return self.render_string('admin/metatags/admin_metatags.html', menu_tab_active='tab_metatags',
                                  platforms=self.session.query(Platform).order_by(Platform.id))
