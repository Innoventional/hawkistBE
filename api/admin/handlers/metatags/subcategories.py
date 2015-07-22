import datetime
import logging
from sqlalchemy import func, and_
from api.admin.handlers.tags import AdminBaseHandler
from api.items.models import Listing
from api.tags.models import Category, Subcategory
from base import HttpRedirect
from helpers import route
from ui_messages.errors.admin_errors.tags_errors import ADMIN_TAG_EMPTY_TITLE, ADMIN_TAG_EMPTY_PARENT, \
    ADMIN_TAG_DOES_NOT_EXIST, ADMIN_SUBCATEGORY_ALREADY_EXISTS, ADMIN_TRY_DELETE_SUBCATEGORY_WHICH_IS_USED

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('/admin/metatags/subcategories')
class AdminSubcategoryHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        subcategories = self.session.query(Subcategory).order_by(Subcategory.id)

        return self.render_string('admin/metatags/admin_subcategories.html', subcategories=subcategories,
                                  categories=self.session.query(Category).order_by(Category.title),
                                  menu_tab_active='tab_metatags')

    def create(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        new_subcategory_title = self.get_argument('new_subcategory_title')
        category_id = self.get_argument('category_id')

        if not new_subcategory_title:
            return self.make_error(ADMIN_TAG_EMPTY_TITLE % 'subcategory')

        if not category_id:
            return self.make_error(ADMIN_TAG_EMPTY_PARENT % 'category')

        category = self.session.query(Category).filter(Category.id == category_id).first()
        if not category:
            return self.make_error(ADMIN_TAG_DOES_NOT_EXIST % ('category', category_id))

        already_exists = self.session.query(Subcategory).filter(and_(func.lower(Subcategory.title) == new_subcategory_title.lower(),
                                                                     Subcategory.category == category)).first()

        if already_exists:
            return self.make_error(ADMIN_SUBCATEGORY_ALREADY_EXISTS % (new_subcategory_title.upper(),
                                                                       category.title.upper(),
                                                                       category.platform.title.upper()))

        new_subcategory = Subcategory()
        new_subcategory.created_at = datetime.datetime.utcnow()
        new_subcategory.updated_at = datetime.datetime.utcnow()
        new_subcategory.title = new_subcategory_title
        new_subcategory.category = category
        self.session.add(new_subcategory)
        self.session.commit()
        return self.success()

    def update(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        subcategory_id = self.get_argument('subcategory_id')
        subcategory_title = self.get_argument('subcategory_title')
        category_id = self.get_argument('category_id')

        if not subcategory_id:
            return self.make_error("Empty subcategory id. Backend failure")

        if not subcategory_title:
            return self.make_error(ADMIN_TAG_EMPTY_TITLE % 'subcategory')

        if not category_id:
            return self.make_error("Empty category id. Backend failure")

        subcategory = self.session.query(Subcategory).filter(Subcategory.id == subcategory_id).first()
        if not subcategory:
            return self.make_error(ADMIN_TAG_DOES_NOT_EXIST % ('subcategory', subcategory_id))

        category = self.session.query(Category).filter(Category.id == category_id).first()
        if not category:
            return self.make_error(ADMIN_TAG_DOES_NOT_EXIST % ('category', category_id))

        already_exists = self.session.query(Subcategory).filter(and_(func.lower(Subcategory.title) == subcategory_title.lower(),
                                                                     Subcategory.category == category,
                                                                     Subcategory.id != subcategory.id)).first()

        if already_exists:
            return self.make_error(ADMIN_SUBCATEGORY_ALREADY_EXISTS % (subcategory.title.upper(),
                                                                       category.platform.title.upper(),
                                                                       category.title.upper()))

        need_commit = False
        # check is title change
        if subcategory.title != subcategory_title:
            subcategory.title = subcategory_title
            need_commit = True

        # check is parent platform change
        if subcategory.category != category:
            subcategory.category = category
            need_commit = True

        if need_commit:
            subcategory.updated_at = datetime.datetime.utcnow()
            self.session.commit()

        return self.success()

    def remove(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        subcategory_id = self.get_arg('subcategory_id')
        subcategory = self.session.query(Subcategory).filter(Subcategory.id == subcategory_id).first()

        if not subcategory:
            return self.make_error(ADMIN_TAG_DOES_NOT_EXIST % ('subcategory', subcategory_id))

        # check is this platform using
        used = self.session.query(Listing).filter(Listing.subcategory == subcategory).first()
        if used:
            return self.make_error(ADMIN_TRY_DELETE_SUBCATEGORY_WHICH_IS_USED % (subcategory.title.upper(),
                                                                                 subcategory.category.platform.title.upper(),
                                                                                 subcategory.category.title.upper()))
        self.session.delete(subcategory)
        self.session.commit()
        return self.success()
