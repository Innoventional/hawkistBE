import datetime
from sqlalchemy import func, and_
from api.admin.handlers.tags import AdminBaseHandler
from api.tags.models import Color, Subcategory
from base import HttpRedirect
from helpers import route

__author__ = 'ne_luboff'


@route('/admin/metatags/colours')
class AdminColourHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'POST')

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        colours = self.session.query(Color).order_by(Color.id)

        return self.render_string('admin/metatags/admin_colours.html', colours=colours,
                                  subcategories=self.session.query(Subcategory).order_by(Subcategory.title),
                                  menu_tab_active='tab_metatags')

    def create(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        new_colour_title = self.get_argument('new_colour_title').lower()
        subcategory_id = self.get_argument('subcategory_id')
        new_colour_code = self.get_argument('new_colour_code')
        disable_color = self.get_argument('disable_colour')

        if not new_colour_title:
            return self.make_error('You must input new colour title')

        if not subcategory_id:
            return self.make_error('You must select subcategory')

        subcategory = self.session.query(Subcategory).filter(Subcategory.id == subcategory_id).first()
        if not subcategory:
            return self.make_error('No category with id %s' % subcategory_id)

        if disable_color == 'true':
            new_colour_code = 'disabled_color'

        already_exists = self.session.query(Color).filter(and_(func.lower(Color.title) == new_colour_title,
                                                               Color.subcategory == subcategory,
                                                               Color.code == new_colour_code)).first()

        if already_exists:
            return self.make_error('Color with name %s already exists in subcategory %s (%s -> %s)'
                                   % (new_colour_title.upper(), subcategory.title.upper(),
                                      subcategory.category.platform.title.upper(), subcategory.category.title.upper()))

        new_color = Color()
        new_color.created_at = datetime.datetime.utcnow()
        new_color.updated_at = datetime.datetime.utcnow()
        new_color.title = new_colour_title
        new_color.code = new_colour_code
        new_color.subcategory = subcategory
        self.session.add(new_color)
        self.session.commit()
        return self.success()
