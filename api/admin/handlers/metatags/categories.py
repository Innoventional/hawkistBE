import datetime
from sqlalchemy import func, and_
from api.admin.handlers.tags import AdminBaseHandler
from api.tags.models import Category, Platform
from base import HttpRedirect, paginate
from helpers import route

__author__ = 'ne_luboff'


@route('/admin/metatags/categories')
class AdminCategoryHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'POST')

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        categories = self.session.query(Category).order_by(Category.id)

        return self.render_string('admin/metatags/admin_categories.html', categories=categories,
                                  platforms=self.session.query(Platform).order_by(Platform.title),
                                  menu_tab_active='tab_metatags')

    def create(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        new_category_title = self.get_argument('new_category_title').lower()
        platform_id = self.get_argument('platform_id')

        if not new_category_title:
            return self.make_error('You must input new category title')

        if not platform_id:
            return self.make_error('You must select platform')

        platform = self.session.query(Platform).filter(Platform.id == platform_id).first()
        if not platform:
            return self.make_error('No platform with id %s' % platform_id)

        already_exists = self.session.query(Category).filter(and_(func.lower(Category.title) == new_category_title,
                                                                  Category.platform == platform)).first()

        if already_exists:
            return self.make_error('Category with name %s already exists in platform %s' % (new_category_title.upper(),
                                                                                            platform.title.upper()))

        new_category = Category()
        new_category.created_at = datetime.datetime.utcnow()
        new_category.updated_at = datetime.datetime.utcnow()
        new_category.title = new_category_title
        new_category.platform = platform
        self.session.add(new_category)
        self.session.commit()
        return self.success()