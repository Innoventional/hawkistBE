import logging
from api.tags.models import Tag, Platform
from base import ApiHandler, die
from helpers import route
from utility.user_utility import check_user_suspension_status, update_user_last_activity

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


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


@route('metatags')
class MetaTagsHandler(ApiHandler):
    allowed_methods = ('GET', )

    def read(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        response = dict()
        # get platform tags
        platforms = self.session.query(Platform).order_by(Platform.title)
        response_by_platform = []
        for p in platforms:
            p_response = p.response
            # get categories by platform
            platform_categories = p.category_platform
            if platform_categories:
                cat_response = []
                for p_c in platform_categories:
                    pc_response = p_c.response
                    # get subcategories by categories
                    category_subcategories = p_c.subcategory_category
                    if category_subcategories:
                        subcat_response = []
                        for c_s in category_subcategories:
                            c_s_response = c_s.response
                            # next get all colour tags
                            subcategories_color = c_s.color_subcategory
                            if subcategories_color:
                                color_response = []
                                for s_col in subcategories_color:
                                    s_col_response = s_col.response
                                    color_response.append(s_col_response)
                                c_s_response['color'] = color_response
                            # and condition tags
                            subcategories_condition = c_s.condition_subcategory
                            if subcategories_condition:
                                condition_response = []
                                for s_con in subcategories_condition:
                                    condition_response.append(s_con.response)
                                c_s_response['condition'] = condition_response
                            subcat_response.append(c_s_response)
                        pc_response['subcategories'] = subcat_response
                    cat_response.append(pc_response)
                p_response['categories'] = cat_response
            response_by_platform.append(p_response)
        response['platforms'] = response_by_platform

        return self.success({'tags': response})
