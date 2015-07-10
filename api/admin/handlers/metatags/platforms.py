import datetime
from sqlalchemy import func, and_
from api.admin.handlers.tags import AdminBaseHandler
from api.items.models import Listing
from api.tags.models import Platform
from base import HttpRedirect
from helpers import route

__author__ = 'ne_luboff'


@route('/admin/metatags/platforms')
class AdminPlatformHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        platforms = self.session.query(Platform).order_by(Platform.id)

        return self.render_string('admin/metatags/admin_platforms.html', platforms=platforms,
                                  menu_tab_active='tab_metatags')

    def create(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        new_platform_title = self.get_argument('new_platform_title')

        if not new_platform_title:
            return self.make_error('You must input new tag title')

        already_exists = self.session.query(Platform).filter(func.lower(Platform.title) == new_platform_title.lower()).first()

        if already_exists:
            return self.make_error('Platform with name %s already exists' % new_platform_title.upper())

        new_platform = Platform()
        new_platform.created_at = datetime.datetime.utcnow()
        new_platform.updated_at = datetime.datetime.utcnow()
        new_platform.title = new_platform_title
        self.session.add(new_platform)
        self.session.commit()
        return self.success()

    def update(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        platform_id = self.get_argument('platform_id')
        platform_title = self.get_argument('platform_title')

        if not platform_id:
            return self.make_error("Empty platform id. Backend failure")

        if not platform_title:
            return self.make_error("You can't delete platform title")

        platform = self.session.query(Platform).filter(Platform.id == platform_id).first()
        if not platform:
            return self.make_error('No platform with id %s' % platform_id)

        already_exists = self.session.query(Platform).filter(and_(func.lower(Platform.title) == platform_title.lower(),
                                                                  Platform.id != platform.id)).first()

        if already_exists:
            return self.make_error('Platform with name %s already exists' % platform_title.upper())

        # check is title change
        if platform.title != platform_title:
            platform.title = platform_title
            platform.updated_at = datetime.datetime.utcnow()
            self.session.commit()

        return self.success()

    def remove(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        platform_id = self.get_arg('platform_id')
        platform = self.session.query(Platform).filter(Platform.id == platform_id).first()

        if not platform:
            return self.make_error('Platform which you try to delete does not exists')

        # check is this platform using
        used = self.session.query(Listing).filter(Listing.platform == platform).first()
        if used:
            return self.make_error('Can not delete the tag %s because it is in use on an active listing. Please update '
                                   'the tag on the listing and try again.' % platform.title.upper())

        self.session.delete(platform)
        self.session.commit()
        return self.success()