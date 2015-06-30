import logging
import datetime
from api.items.models import Item, ItemPhoto
from base import ApiHandler, die
from helpers import route, sa_object_to_dict

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('items')
class ItemsHandler(ApiHandler):
    allowed_methods = ('POST', )

    def create(self):

        if self.user is None:
            die(401)

        logger.debug('REQUEST_OBJECT_NEW_ITEM')
        logger.debug(self.request_object)

        title = ''
        description = ''
        platform = ''
        category = ''
        condition = ''
        color_list = ''
        retail_price = ''
        selling_price = ''
        shipping_price = ''
        collection_only = ''
        barcode = ''
        photos = ''

        if 'title' in self.request_object:
            title = self.request_object['title']

        if 'description' in self.request_object:
            description = self.request_object['description']

        if 'platform' in self.request_object:
            platform = self.request_object['platform']

        if 'category' in self.request_object:
            category = self.request_object['category']

        if 'condition' in self.request_object:
            condition = self.request_object['condition']

        if 'color' in self.request_object:
            color_list = self.request_object['color']

        if 'retail_price' in self.request_object:
            retail_price = self.request_object['retail_price']

        if 'selling_price' in self.request_object:
            selling_price = self.request_object['selling_price']

        if 'shipping_price' in self.request_object:
            shipping_price = self.request_object['shipping_price']

        if 'collection_only' in self.request_object:
            collection_only = self.request_object['collection_only']

        if 'barcode' in self.request_object:
            barcode = self.request_object['barcode']

        if 'photos' in self.request_object:
            photos = self.request_object['photos']

        if not title:
            return self.make_error('Undefined item title')

        if not description:
            return self.make_error('Undefined item description')

        if not platform:
            return self.make_error('Undefined item platform')

        if not category:
            return self.make_error('Undefined item category')

        if not condition:
            return self.make_error('Undefined item condition')

        if not color_list:
            return self.make_error('Undefined item colour')

        if not retail_price:
            return self.make_error('Undefined item price')

        if not shipping_price and not collection_only:
            return self.make_error('You must choose one of shipping options:\n'
                                   'enter shipping price or select collection only flag')

        # if not barcode:
        #     return self.make_error('Undefined item barcode')

        if not photos:
            return self.make_error('Undefined item photos')

        item = Item()
        item.user = self.user
        item.created_at = datetime.datetime.utcnow()
        item.updated_at = datetime.datetime.utcnow()
        item.title = title
        item.description = description

        if barcode:
            item.barcode = barcode

        # check platforms
        if platform not in [i for i in xrange(6)]:
            return self.make_error('Invalid platform')

        item.platform = platform

        # check category
        if category not in [i for i in xrange(4)]:
            return self.make_error('Invalid category')

        item.category = category

        # check condition
        if condition not in [i for i in xrange(5)]:
            return self.make_error('Invalid condition')

        item.condition = condition

        # color check
        # check is OTHER or NOT APPLICABLE in selected color list with other colors
        if len(color_list) > 1:
            if 8 in color_list:
                return self.make_error("You can't choose OTHER tag with other options")
            elif 9 in color_list:
                return self.make_error("You can't choose NOT APPLICABLE tag with other options")

        item_color_field = []
        for color in color_list:
            if color not in [i for i in xrange(10)]:
                return self.make_error('Invalid colour')
            item_color_field.append(color)
        item.color = str(item_color_field).replace('[', '').replace(']', '')

        # price handler
        item.retail_price = retail_price
        if selling_price:
            if selling_price == retail_price:
                return self.make_error("Retail and selling prices are the same!")
            if selling_price > retail_price:
                return self.make_error("Selling price can't be more than retail price!")
            item.selling_price = selling_price
            # calculate discount value
            discount = int(round((retail_price - selling_price) / retail_price * 100))
            item.discount = discount

        self.session.flush(item)
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
        return self.success({'item': sa_object_to_dict(item)})
