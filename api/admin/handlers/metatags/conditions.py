import datetime
from sqlalchemy import and_
from sqlalchemy import func
from api.admin.handlers.tags import AdminBaseHandler
from api.tags.models import Color, Condition, Subcategory
from base import HttpRedirect
from helpers import route

__author__ = 'ne_luboff'


@route('/admin/metatags/conditions')
class AdminConditionHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'POST')

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        conditions = self.session.query(Condition).order_by(Condition.id)

        return self.render_string('admin/metatags/admin_conditions.html', conditions=conditions,
                                  subcategories=self.session.query(Subcategory).order_by(Subcategory.title),
                                  menu_tab_active='tab_metatags')

    def create(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        new_condition_title = self.get_argument('new_condition_title').lower()
        subcategory_id = self.get_argument('subcategory_id')

        if not new_condition_title:
            return self.make_error('You must input new condition title')

        if not subcategory_id:
            return self.make_error('You must select subcategory')

        subcategory = self.session.query(Subcategory).filter(Subcategory.id == subcategory_id).first()
        if not subcategory:
            return self.make_error('No category with id %s' % subcategory_id)

        already_exists = self.session.query(Condition).filter(and_(func.lower(Condition.title) == new_condition_title,
                                                                   Condition.subcategory == subcategory)).first()

        if already_exists:
            return self.make_error('Condition with name %s already exists in subcategory %s (%s -> %s)'
                                   % (new_condition_title.upper(), subcategory.title.upper(),
                                      subcategory.category.platform.title.upper(), subcategory.category.title.upper()))

        new_condition = Condition()
        new_condition.created_at = datetime.datetime.utcnow()
        new_condition.updated_at = datetime.datetime.utcnow()
        new_condition.title = new_condition_title
        new_condition.subcategory = subcategory
        self.session.add(new_condition)
        self.session.commit()
        return self.success()
