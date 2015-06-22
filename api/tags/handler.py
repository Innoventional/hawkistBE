from api.tags.models import Tag
from base import ApiHandler, die
from helpers import route

__author__ = 'ne_luboff'


@route('tags')
class TagsHandler(ApiHandler):
    allowed_methods = ('GET', )

    def read(self):
        if self.user is None:
            die(401)

        all_tags = self.session.query(Tag).order_by(Tag.id)
        return self.success({'tags': [tag.tag_response for tag in all_tags]})
