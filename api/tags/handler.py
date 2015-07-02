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

        # first of all get all parent tag
        # parent means tag haven't child tags
        response = []
        parent_tags = self.session.query(Tag).filter(Tag.parent_tag_id == None).order_by(Tag.id)
        # for every parent get children
        for parent in parent_tags:
            current_response = parent.tag_response
            children1 = parent.children_tags
            if children1.count() != 0:
                current_response['children'] = []
                for child1 in children1:
                    child1_response = child1.tag_response
                    # for every child1 get children
                    children2 = child1.children_tags
                    if children2.count() != 0:
                        child1_response['children'] = []
                        for child2 in children2:
                            child2_response = child2.tag_response
                            child1_response['children'].append(child2_response)
                            children3 = child2.children_tags
                            if children3.count() != 0:
                                child2_response['children'] = []
                                for child3 in children3:
                                    child3_response = child3.tag_response
                                    child2_response['children'].append(child3_response)
                    current_response['children'].append(child1_response)
            response.append(current_response)

        return self.success({'tags': response})


def get_children(tag):
    if tag.children_tags:
        print [i.name for i in tag.children_tags]
    return tag.children_tags
