import datetime
from sqlalchemy import func, and_
from api.admin.handlers.tags import AdminBaseHandler
from api.items.models import Listing
from api.tags.models import Category, Platform
from base import HttpRedirect
from helpers import route

__author__ = 'ne_luboff'


@route('/admin/metatags/categories')
class AdminCategoryHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

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

        new_category_title = self.get_argument('new_category_title')
        platform_id = self.get_argument('platform_id')

        if not new_category_title:
            return self.make_error('You must input new category title')

        if not platform_id:
            return self.make_error('You must select platform')

        platform = self.session.query(Platform).filter(Platform.id == platform_id).first()
        if not platform:
            return self.make_error('No platform with id %s' % platform_id)

        already_exists = self.session.query(Category).filter(and_(func.lower(Category.title) == new_category_title.lower(),
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

    def update(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        category_id = self.get_argument('category_id')
        category_title = self.get_argument('category_title')
        platform_id = self.get_argument('platform_id')

        if not category_id:
            return self.make_error("Empty category id. Backend failure")

        if not category_title:
            return self.make_error("You can't delete category title")

        if not platform_id:
            return self.make_error("Empty platform id. Backend failure")

        category = self.session.query(Category).filter(Category.id == category_id).first()
        if not category:
            return self.make_error('No category with id %s' % category_id)

        platform = self.session.query(Platform).filter(Platform.id == platform_id).first()
        if not platform:
            return self.make_error('No platform with id %s' % platform_id)

        already_exists = self.session.query(Category).filter(and_(func.lower(Category.title) == category_title.lower(),
                                                                  Category.platform == platform,
                                                                  Category.id != category.id)).first()

        if already_exists:
            return self.make_error('Category with name %s already exists in platform %s' % (category.title.upper(),
                                                                                            platform.title.upper()))

        need_commit = False
        # check is title change
        if category.title != category_title:
            category.title = category_title
            need_commit = True

        # check is parent platform change
        if category.platform != platform:
            category.platform = platform
            need_commit = True

        if need_commit:
            category.updated_at = datetime.datetime.utcnow()
            self.session.commit()

        return self.success()

    def remove(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        category_id = self.get_arg('category_id')
        category = self.session.query(Category).filter(Category.id == category_id).first()

        if not category:
            return self.make_error('Category which you try to delete does not exists')

        # check is this platform using
        used = self.session.query(Listing).filter(Listing.category == category).first()
        if used:
            return self.make_error('Can not delete the tag %s (%s) because it is in use on an active listing. '
                                   'Please update the tag on the listing and try again.'
                                   % (category.title.upper(), category.platform.title.upper()))

        self.session.delete(category)
        self.session.commit()
        return self.success()