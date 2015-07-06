# -*- coding: utf-8 -*-

import logging
import datetime
from sqlalchemy import or_, desc
from api.items.models import Item, ItemPhoto
from api.tags.models import Tag
from base import ApiHandler, die, paginate
from helpers import route, sa_object_to_dict
from utility.google_api import get_city_by_code

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('user/items')
class ItemsHandler(ApiHandler):
    allowed_methods = ('GET', 'POST', )

    def read(self):

        if not self.user:
            die(401)

        user_tags = self.user.user_tags
        if not user_tags:
            return self.make_error("Your feeds are empty 'cause you don't add any tags")

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

        # finally find all ids of interesting user listings
        item_ids = set()
        for tag_id in user_tags_set:
            items_with_this_tag = self.session.query(Item).filter(or_(Item.platform_id == tag_id,
                                                                      Item.category_id == tag_id,
                                                                      Item.subcategory_id == tag_id))
            for item in items_with_this_tag:
                item_ids.add(item.id)

        items = self.session.query(Item).filter(Item.id.in_(list(item_ids))).order_by(desc(Item.id))

        # pagination
        page = self.get_arg('p', int, 1)
        page_size = self.get_arg('page_size', int, 100)
        paginator, listings = paginate(items, page, page_size)

        return self.success({
            'items': [i.item_response for i in listings],
            'paginator': paginator
        })

    def create(self):

        if self.user is None:
            die(401)

        # check selling ability
        if not self.user.facebook_id:
            return self.make_error("Sorry, but you can't sale anything 'cause you don't link your FB account")
        if not self.user.email_status:
            return self.make_error("Sorry, but you can't sale anything 'cause you don't confirm your email address")

        logger.debug('REQUEST_OBJECT_NEW_ITEM')
        logger.debug(self.request_object)

        title = ''
        description = ''
        platform_id = ''
        category_id = ''
        subcategory_id = ''
        condition_id = ''
        color_id = ''
        retail_price = ''
        selling_price = ''
        shipping_price = ''
        collection_only = ''
        barcode = ''
        photos = ''
        post_code = ''
        city = ''

        empty_field_error = []

        if self.request_object:
            if 'title' in self.request_object:
                title = self.request_object['title']

            if 'description' in self.request_object:
                description = self.request_object['description']

            if 'platform' in self.request_object:
                platform_id = self.request_object['platform']

            if 'category' in self.request_object:
                category_id = self.request_object['category']

            if 'subcategory' in self.request_object:
                subcategory_id = self.request_object['subcategory']

            if 'condition' in self.request_object:
                condition_id = self.request_object['condition']

            if 'color' in self.request_object:
                color_id = self.request_object['color']

            if 'retail_price' in self.request_object:
                retail_price = float(self.request_object['retail_price'])

            if 'selling_price' in self.request_object:
                selling_price = float(self.request_object['selling_price'])

            if 'shipping_price' in self.request_object:
                shipping_price = float(self.request_object['shipping_price'])

            if 'collection_only' in self.request_object:
                collection_only = self.request_object['collection_only']

            if 'barcode' in self.request_object:
                barcode = self.request_object['barcode']

            if 'photos' in self.request_object:
                photos = self.request_object['photos']

            if 'post_code' in self.request_object:
                post_code = self.request_object['post_code']

            if 'city' in self.request_object:
                city = self.request_object['city']

        if not title:
            empty_field_error.append('title')

        if not description:
            empty_field_error.append('description')

        if not platform_id:
            empty_field_error.append('platform')

        if not category_id:
            empty_field_error.append('category')

        if not subcategory_id:
            empty_field_error.append('subcategory')

        if not condition_id:
            empty_field_error.append('condition')

        if not color_id:
            empty_field_error.append('color')

        if not retail_price:
            empty_field_error.append('retail price')

        if not selling_price:
            empty_field_error.append('selling price')

        if not shipping_price:
            empty_field_error.append('shipping price')

        # if not collection_only:
        #     empty_field_error.append('collection only flag')

        if not photos:
            empty_field_error.append('photos')

        for photo in photos:
            if not photo:
                empty_field_error.append('photos')
                break

        if not post_code:
            empty_field_error.append('post code')

        if not city:
            empty_field_error.append('city')

        if empty_field_error:
            empty_fields = ','.join(empty_field_error)
            return {
                'status': 6,
                'message': 'You must select a %s in order to create a listing.' % empty_fields,
                'empty_fields': empty_fields
            }

        # first check all tags
        # check platforms
        platform = self.session.query(Tag).filter(Tag.id == platform_id).first()
        if not platform:
            return self.make_error('No platform with id %s' % platform_id)

        # check category
        category = self.session.query(Tag).filter(Tag.id == category_id).first()
        if not category:
            return self.make_error('No category with id %s' % category_id)

        # check subcategory
        subcategory = self.session.query(Tag).filter(Tag.id == subcategory_id).first()
        if not subcategory:
            return self.make_error('No subcategory with id %s' % category_id)

        # check is this nesting right
        platform_children_ids = [child.id for child in platform.children_tags]
        if category_id not in platform_children_ids:
            return self.make_error("Platform tag %s hasn't child %s. Try again" % (platform.name.upper(),
                                                                                   category.name.upper()))
        category_children_ids = [child.id for child in category.children_tags]
        if subcategory_id not in category_children_ids:
            return self.make_error("Category tag %s hasn't child %s. Try again" % (category.name.upper(),
                                                                                   subcategory.name.upper()))

        # check condition
        condition = self.session.query(Tag).filter(Tag.id == condition_id).first()
        if not condition:
            return self.make_error('No condition with id %s' % condition_id)

        # check color
        color = self.session.query(Tag).filter(Tag.id == color_id).first()
        if not color:
            return self.make_error('No color with id %s' % color_id)

        # secondary check other fields
        # price handler
        if retail_price < 1:
            return self.make_error(u'Retail price must be greater than £1')

        if selling_price > retail_price:
                return self.make_error("Retail price must be greater than selling price")

        if len(photos) > 3:
            return self.make_error('You can add only 3 photos')

        # finally create item
        item = Item()
        item.user = self.user
        item.created_at = datetime.datetime.utcnow()
        item.updated_at = datetime.datetime.utcnow()
        item.title = title
        item.description = description

        if barcode:
            item.barcode = barcode

        item.platform_id = platform_id
        item.category_id = category_id
        item.subcategory_id = subcategory_id
        item.condition_id = condition_id
        item.color_id = color_id
        item.retail_price = retail_price
        item.selling_price = selling_price

        if selling_price != retail_price:
            # calculate discount value
            discount = int(round((retail_price - selling_price) / retail_price * 100))
            item.discount = discount

        item.shipping_price = shipping_price
        if collection_only:
            item.collection_only = True
        else:
            item.collection_only = False

        item.post_code = post_code
        item.city = city

        # self.session.flush(item)
        # self.session.commit()

        # photos
        for photo in photos:
            item_photo = ItemPhoto()
            item_photo.created_at = datetime.datetime.utcnow()
            item_photo.item = item
            item_photo.image_url = photo
            self.session.add(item_photo)
            self.session.commit()

        self.session.commit()
        return self.success({'item': item.item_response})


@route('get_city')
class PostCodeHandler(ApiHandler):
    allowed_methods = ('PUT', )

    def update(self):

        if self.user is None:
            die(401)

        logger.debug('REQUEST_OBJECT_GET_CITY_BY_POST_CODE')
        logger.debug(self.request_object)

        post_code = ''

        if 'post_code' in self.request_object:
            post_code = self.request_object['post_code']

        if not post_code:
            return {
                'status': 6,
                'message': 'You must select a post code in order to create a listing.'
            }

        google_response = get_city_by_code(post_code)
        error, data = google_response['error'], google_response['data']
        if error:
            return self.make_error(error)
        return self.success({'city': data})
