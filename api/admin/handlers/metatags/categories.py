import datetime
from sqlalchemy import func, and_
from api.admin.handlers.tags import AdminBaseHandler
from api.items.models import Listing
from api.tags.models import Category, Platform
from base import HttpRedirect
from helpers import route

__author__ = 'ne_luboff'


# route is the path of rest request
@route('/admin/metatags/categories')
class AdminCategoryHandler(AdminBaseHandler):
    # allowed methods - available methods
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

    # function for GET method
    def read(self):
        # check is user authorized
        # (get user id from received cookies)
        if not self.user:
            # if not authorized - redirect user to login page
            return HttpRedirect('/api/admin/login')

        # get all categories from db and sort it by id
        categories = self.session.query(Category).order_by(Category.id)

        # web page rendering
        # first parameter - path to template in project
        # others - data which used to page render
        return self.render_string('admin/metatags/admin_categories.html', categories=categories,
                                  platforms=self.session.query(Platform).order_by(Platform.title),
                                  menu_tab_active='tab_metatags')

    # function for POST method
    def create(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        # get data from post parameters
        new_category_title = self.get_argument('new_category_title')
        platform_id = self.get_argument('platform_id')

        # check is all data fill because all this fields (new category title and parent platform id) are required
        # if one of field is empty - return an error
        if not new_category_title:
            return self.make_error('You must input new category title')

        if not platform_id:
            return self.make_error('You must select platform')

        # check is chosen platform exists
        platform = self.session.query(Platform).filter(Platform.id == platform_id).first()
        if not platform:
            return self.make_error('No platform with id %s' % platform_id)

        # check is category which we want to create already exists in this platform
        # because category title not case sensitive we must compare in lower register
        already_exists = self.session.query(Category).filter(and_(func.lower(Category.title) == new_category_title.lower(),
                                                                  Category.platform == platform)).first()

        if already_exists:
            return self.make_error('Category with name %s already exists in platform %s' % (new_category_title.upper(),
                                                                                            platform.title.upper()))

        # finally in same category not exist create a new one
        new_category = Category()
        new_category.created_at = datetime.datetime.utcnow()
        new_category.updated_at = datetime.datetime.utcnow()
        new_category.title = new_category_title
        new_category.platform = platform
        # add new category instance to session
        self.session.add(new_category)
        # and commit session changes
        self.session.commit()
        return self.success()

    # function for PUT request
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

        # need commit is the flag that show us is something changed in current category info
        # we need it to know must we connect to database  or not
        # less connection to db - more quickly application
        need_commit = False
        # check is title change
        if category.title != category_title:
            category.title = category_title
            need_commit = True

        # check is parent platform change
        if category.platform != platform:
            category.platform = platform
            need_commit = True

        # in category title or parent platform was changes we do session commit
        if need_commit:
            category.updated_at = datetime.datetime.utcnow()
            self.session.commit()

        return self.success()

    # function to DELETE  request
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