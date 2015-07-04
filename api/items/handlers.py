# -*- coding: utf-8 -*-

import logging
import datetime
from api.items.models import Item, ItemPhoto
from api.tags.models import Tag
from base import ApiHandler, die
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

        items = self.session.query(Item).order_by(Item.id)

        return self.success({'items': [i.item_response for i in items]})

    def create(self):

        if self.user is None:
            die(401)

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

        if not collection_only:
            empty_field_error.append('collection only flag')

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

        retail_price_float = float(retail_price)
        selling_price_float = float(selling_price)
        shipping_price_float = float(shipping_price)

        # check all tags

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

        # check condition
        condition = self.session.query(Tag).filter(Tag.id == condition_id).first()
        if not condition:
            return self.make_error('No condition with id %s' % condition_id)

        # check color
        color = self.session.query(Tag).filter(Tag.id == color_id).first()
        if not color:
            return self.make_error('No color with id %s' % color_id)

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

        # price handler
        if retail_price < 1:
            return self.make_error(u'Retail price must be greater than £1')

        item.retail_price = retail_price

        if selling_price > retail_price:
                return self.make_error("Retail price must be greater than selling price")

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
        if len(photos) > 3:
            return self.make_error('You can add only 3 photos')

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
