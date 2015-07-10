import datetime
from sqlalchemy import func, and_, or_
from api.items.models import Item
from api.tags.models import Tag
from base import OpenApiHandler, paginate, HttpRedirect
from helpers import route

__author__ = 'ne_luboff'

class AdminBaseHandler(OpenApiHandler):
    pass


@route('admin/tags')
class AdminTagsHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        tags = self.session.query(Tag).order_by(Tag.id)

        page = self.get_arg('p', int, 1)
        page_size = self.get_arg('page_size', int, 100)

        paginator, tags = paginate(tags, page, page_size)

        return self.render_string('admin/admin_tags.html', tags=tags, paginator=paginator, menu_tab_active='tab_tags')

    def create(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        parent_tag_id = self.get_argument('parent_tag_id')
        new_tag_name = self.get_argument('new_tag_name')

        if not new_tag_name:
            return self.make_error('You must input new tag title')

        if int(parent_tag_id) != 0:
            already_exists = self.session.query(Tag).filter(and_(func.lower(Tag.name) == new_tag_name.lower(),
                                                                 Tag.parent_tag_id == parent_tag_id)).first()
        else:
            already_exists = self.session.query(Tag).filter(and_(func.lower(Tag.name) == new_tag_name.lower(),
                                                                 Tag.parent_tag_id == None)).first()

        if already_exists:
            return self.make_error('Tag with name %s already exists' % new_tag_name.upper())

        new_tag = Tag()
        new_tag.created_at = datetime.datetime.utcnow()
        new_tag.updated_at = datetime.datetime.utcnow()
        new_tag.name = new_tag_name
        if int(parent_tag_id) != 0:
            new_tag.parent_tag_id = parent_tag_id
        self.session.add(new_tag)
        self.session.commit()
        return self.success()

    def update(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        tag_id = self.get_argument('tag_id')
        tag_name = self.get_argument('tag_name')

        parent_tag_id = self.get_argument('parent_tag_id')

        if not tag_name:
            return self.make_error('You must input new tag title')

        if not tag_id or not parent_tag_id:
            return self.make_error('Something wrong. Try again later')

        tag = self.session.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            return self.make_error('Something wrong. Try again later')

        if tag.name != tag_name:
            tag.name = tag_name

        if tag.parent_tag_id != parent_tag_id:
            if parent_tag_id == '0':
                tag.parent_tag_id = None
            else:
                tag.parent_tag_id = parent_tag_id

        tag.updated_at = datetime.datetime.utcnow()
        self.session.commit()
        return self.success()

    def remove(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        tag_id = self.get_arg('tag_id')
        tag = self.session.query(Tag).filter(Tag.id == tag_id).first()

        if not tag:
            return self.make_error('Something wrong. Try again later')
        # check is this tag using
        used = self.session.query(Item).filter(or_(Item.platform_id == tag_id,
                                                   Item.category_id == tag_id,
                                                   Item.subcategory_id == tag_id,
                                                   Item.condition_id == tag_id,
                                                   Item.color_id == tag_id)).first()
        if used:
            return self.make_error('Can not delete the tag %s because it is in use on an active listing. Please update '
                                   'the tag on the listing and try again.' % tag.name.upper())
        self.session.delete(tag)
        self.session.commit()
        return self.success()
