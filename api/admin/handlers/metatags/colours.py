import datetime
from sqlalchemy import func, and_
from api.admin.handlers.tags import AdminBaseHandler
from api.items.models import Listing
from api.tags.models import Color, Subcategory
from base import HttpRedirect
from helpers import route

__author__ = 'ne_luboff'


@route('/admin/metatags/colours')
class AdminColourHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

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

    def update(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        colour_id = self.get_argument('colour_id')
        colour_title = self.get_argument('colour_title').lower()
        subcategory_id = self.get_argument('subcategory_id')
        colour_code = self.get_argument('colour_code')
        disable_colour = self.get_argument('disable_colour')

        if not colour_id:
            return self.make_error("Empty colour id. Backend failure")

        if not colour_code:
            return self.make_error("Empty colour code. Backend failure")

        if not colour_title:
            return self.make_error("You can't delete colour title")

        if not subcategory_id:
            return self.make_error("Empty subcategory id. Backend failure")

        colour = self.session.query(Color).filter(Color.id == colour_id).first()
        if not colour:
            return self.make_error('No colour with id %s' % colour_id)

        subcategory = self.session.query(Subcategory).filter(Subcategory.id == subcategory_id).first()
        if not subcategory:
            return self.make_error('No subcategory with id %s' % subcategory_id)

        if disable_colour == 'true':
            colour_code = 'disabled_color'

        already_exists = self.session.query(Color).filter(and_(func.lower(Color.title) == colour_title,
                                                               Color.code == colour_code,
                                                               Color.subcategory == subcategory,
                                                               Color.id != colour.id)).first()

        if already_exists:
            return self.make_error('Colour with name %s already exists in subcategory (%s > %s > %s)'
                                   % (colour.title.upper(), subcategory.category.platform.title.upper(),
                                      subcategory.category.title.upper(), subcategory.title.upper()))

        need_commit = False
        # check is title change
        if colour.title != colour_title:
            colour.title = colour_title
            need_commit = True

        # check is parent subcategory change
        if colour.subcategory != subcategory:
            colour.subcategory = subcategory
            need_commit = True

        # check is colour code change
        if colour.code != colour_code:
            colour.code = colour_code
            need_commit = True

        if need_commit:
            colour.updated_at = datetime.datetime.utcnow()
            self.session.commit()

        return self.success()

    def remove(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        colour_id = self.get_arg('colour_id')
        colour = self.session.query(Color).filter(Color.id == colour_id).first()

        if not colour:
            return self.make_error('Colour which you try to delete does not exists')

        # check is this colour using
        used = self.session.query(Listing).filter(Listing.color == colour).first()
        if used:
            return self.make_error('Can not delete the tag %s (%s > %s > %s) because it is in use on an active listing. '
                                   'Please update the tag on the listing and try again.'
                                   % (colour.title.upper(), colour.subcategory.category.platform.title.upper(),
                                      colour.subcategory.category.title.upper(), colour.subcategory.title.upper()))

        self.session.delete(colour)
        self.session.commit()
        return self.success()
