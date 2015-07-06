import logging
from sqlalchemy import or_
from api.items.models import Item

__author__ = 'ne_luboff'

# get interested user tags ids
logger = logging.getLogger(__name__)


def interested_user_tag_ids(self):
    user_tags = self.user.user_tags
    if not user_tags:
        logger.debug("User %s hasn't tags" % self.user.id)

    # check have user tags children
    # create set with user tags
    user_tags_set = set()
    for tag in user_tags:
        user_tags_set.add(tag.id)
        children1 = tag.tag.children_tags
        if children1.count != 0:
            for ch1 in children1:
                user_tags_set.add(ch1.id)
                children2 = ch1.children_tags
                if children2.count != 0:
                    for ch2 in children2:
                        user_tags_set.add(ch2.id)
    return user_tags_set


def interested_user_item_ids(self, user_tags):
    item_ids = set()
    for tag_id in user_tags:
        items_with_this_tag = self.session.query(Item).filter(or_(Item.platform_id == tag_id,
                                                                  Item.category_id == tag_id,
                                                                  Item.subcategory_id == tag_id))
        for item in items_with_this_tag:
            item_ids.add(item.id)
    return item_ids
