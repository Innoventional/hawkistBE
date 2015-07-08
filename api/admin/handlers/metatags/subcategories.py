from operator import and_
import datetime
from sqlalchemy import func
from api.admin.handlers.tags import AdminBaseHandler
from api.tags.models import Category, Subcategory
from base import HttpRedirect
from helpers import route

__author__ = 'ne_luboff'


@route('/admin/metatags/subcategories')
class AdminSubcategoryHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'POST')

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        subcategories = self.session.query(Subcategory).order_by(Subcategory.id)

        return self.render_string('admin/metatags/admin_subcategories.html', subcategories=subcategories,
                                  categories=self.session.query(Category).order_by(Category.title),
                                  menu_tab_active='tab_metatags')

    def create(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        new_subcategory_title = self.get_argument('new_subcategory_title').lower()
        category_id = self.get_argument('category_id')

        if not new_subcategory_title:
            return self.make_error('You must input new category title')

        if not category_id:
            return self.make_error('You must select platform')

        category = self.session.query(Category).filter(Category.id == category_id).first()
        if not category:
            return self.make_error('No category with id %s' % category_id)

        already_exists = self.session.query(Subcategory).filter(and_(func.lower(Subcategory.title) == new_subcategory_title,
                                                                     Subcategory.category == category)).first()

        if already_exists:
            return self.make_error('Subcategory with name %s already exists in category %s' % (new_subcategory_title.upper(),
                                                                                               category.title.upper()))

        new_subcategory = Subcategory()
        new_subcategory.created_at = datetime.datetime.utcnow()
        new_subcategory.updated_at = datetime.datetime.utcnow()
        new_subcategory.title = new_subcategory_title
        new_subcategory.category = category
        self.session.add(new_subcategory)
        self.session.commit()
        return self.success()
