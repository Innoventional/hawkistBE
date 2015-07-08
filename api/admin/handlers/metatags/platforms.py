import datetime
from sqlalchemy import func
from api.admin.handlers.tags import AdminBaseHandler
from api.tags.models import Platform
from base import HttpRedirect
from helpers import route

__author__ = 'ne_luboff'


@route('/admin/metatags/platforms')
class AdminPlatformHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'POST')

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        platforms = self.session.query(Platform).order_by(Platform.id)

        return self.render_string('admin/metatags/admin_platforms.html', platforms=platforms,
                                  menu_tab_active='tab_metatags')

    def create(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        new_platform_title = self.get_argument('new_platform_title').lower()

        if not new_platform_title:
            return self.make_error('You must input new tag title')

        already_exists = self.session.query(Platform).filter(func.lower(Platform.title) == new_platform_title).first()

        if already_exists:
            return self.make_error('Platform with name %s already exists' % new_platform_title.upper())

        new_platform = Platform()
        new_platform.created_at = datetime.datetime.utcnow()
        new_platform.updated_at = datetime.datetime.utcnow()
        new_platform.title = new_platform_title
        self.session.add(new_platform)
        self.session.commit()
        return self.success()