import datetime
from sqlalchemy import and_
from sqlalchemy import func
from api.admin.handlers.tags import AdminBaseHandler
from api.items.models import Listing
from api.tags.models import Condition, Subcategory
from base import HttpRedirect
from helpers import route
from ui_messages.errors.admin_errors.tags_errors import ADMIN_TAG_EMPTY_TITLE, ADMIN_TAG_EMPTY_PARENT, \
    ADMIN_TAG_DOES_NOT_EXIST, ADMIN_CONDITION_ALREADY_EXISTS, ADMIN_TRY_DELETE_CONDITION_WHICH_IS_USED

__author__ = 'ne_luboff'


@route('/admin/metatags/conditions')
class AdminConditionHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

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

        new_condition_title = self.get_argument('new_condition_title')
        subcategory_id = self.get_argument('subcategory_id')

        if not new_condition_title:
            return self.make_error(ADMIN_TAG_EMPTY_TITLE % 'condition')

        if not subcategory_id:
            return self.make_error(ADMIN_TAG_EMPTY_PARENT % 'subcategory')

        subcategory = self.session.query(Subcategory).filter(Subcategory.id == subcategory_id).first()
        if not subcategory:
            return self.make_error(ADMIN_TAG_DOES_NOT_EXIST % ('subcategory', subcategory_id))

        already_exists = self.session.query(Condition).filter(and_(func.lower(Condition.title) == new_condition_title.lower(),
                                                                   Condition.subcategory == subcategory)).first()

        if already_exists:
            return self.make_error(ADMIN_CONDITION_ALREADY_EXISTS % (new_condition_title.upper(),
                                                                     subcategory.title.upper(),
                                                                     subcategory.category.platform.title.upper(),
                                                                     subcategory.category.title.upper()))

        new_condition = Condition()
        new_condition.created_at = datetime.datetime.utcnow()
        new_condition.updated_at = datetime.datetime.utcnow()
        new_condition.title = new_condition_title
        new_condition.subcategory = subcategory
        self.session.add(new_condition)
        self.session.commit()
        return self.success()

    def update(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        condition_id = self.get_argument('condition_id')
        condition_title = self.get_argument('condition_title')
        subcategory_id = self.get_argument('subcategory_id')

        if not condition_id:
            return self.make_error("Empty condition id. Backend failure")

        if not condition_title:
            return self.make_error(ADMIN_TAG_EMPTY_TITLE % 'condition')

        if not subcategory_id:
            return self.make_error("Empty subcategory id. Backend failure")

        condition = self.session.query(Condition).filter(Condition.id == condition_id).first()
        if not condition:
            return self.make_error(ADMIN_TAG_DOES_NOT_EXIST % ('condition', condition_id))

        subcategory = self.session.query(Subcategory).filter(Subcategory.id == subcategory_id).first()
        if not subcategory:
            return self.make_error(ADMIN_TAG_DOES_NOT_EXIST % ('subcategory', subcategory_id))

        already_exists = self.session.query(Condition).filter(and_(func.lower(Condition.title) == condition_title.lower(),
                                                                   Condition.subcategory == subcategory,
                                                                   Condition.id != condition.id)).first()

        if already_exists:
            return self.make_error(ADMIN_CONDITION_ALREADY_EXISTS % (condition.title.upper(),
                                                                     subcategory.title.upper(),
                                                                     subcategory.category.platform.title.upper(),
                                                                     subcategory.category.title.upper()))

        need_commit = False
        # check is title change
        if condition.title != condition_title:
            condition.title = condition_title
            need_commit = True

        # check is parent subcategory change
        if condition.subcategory != subcategory:
            condition.subcategory = subcategory
            need_commit = True

        if need_commit:
            condition.updated_at = datetime.datetime.utcnow()
            self.session.commit()

        return self.success()

    def remove(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        condition_id = self.get_arg('condition_id')
        condition = self.session.query(Condition).filter(Condition.id == condition_id).first()

        if not condition:
            return self.make_error(ADMIN_TAG_DOES_NOT_EXIST % ('condition', condition_id))

        # check is this colour using
        used = self.session.query(Listing).filter(Listing.condition == condition).first()
        if used:
            return self.make_error(ADMIN_TRY_DELETE_CONDITION_WHICH_IS_USED % (condition.title.upper(),
                                                                               condition.subcategory.category.platform.title.upper(),
                                                                               condition.subcategory.category.title.upper(),
                                                                               condition.subcategory.title.upper()))
        self.session.delete(condition)
        self.session.commit()
        return self.success()

