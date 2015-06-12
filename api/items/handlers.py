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
        condition = ''
        color = ''
        barcode = ''
        photos = ''
        warning_message = ''

        if 'title' in self.request_object:
            title = self.request_object['title']

        if 'description' in self.request_object:
            description = self.request_object['description']

        if 'condition' in self.request_object:
            condition = self.request_object['condition']

        if 'color' in self.request_object:
            color = self.request_object['color']

        if 'barcode' in self.request_object:
            barcode = self.request_object['barcode']

        if 'photos' in self.request_object:
            photos = self.request_object['photos']

        if not title:
            return self.make_error('Undefined item title')

        if not description:
            return self.make_error('Undefined item description')

        if not barcode:
            return self.make_error('Undefined item barcode')

        if not photos:
            return self.make_error('Undefined item photos')

        item = Item()
        item.user = self.user
        item.created_at = datetime.datetime.utcnow()
        item.updated_at = datetime.datetime.utcnow()
        item.title = title
        item.description = description
        item.barcode = barcode
        if color:
            item.color = color
        if condition:
            item.condition = condition

        self.session.add(item)
        self.session.commit()

        for photo in photos:
            # check number of photo
            photo_count = self.session.query(ItemPhoto).filter(ItemPhoto.item == item).count()
            if photo_count > 4:
                warning_message = 'Item can have only 4 photos'
                logger.debug(warning_message)
            item_photo = ItemPhoto()
            item_photo.created_at = datetime.datetime.utcnow()
            item_photo.item = item
            item_photo.image_url = photo
            self.session.add(item_photo)
            self.session.commit()

        response = self.success({'item': sa_object_to_dict(item)})
        if warning_message:
            response['warning'] = warning_message
        return response
