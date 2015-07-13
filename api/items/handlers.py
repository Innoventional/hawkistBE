# -*- coding: utf-8 -*-

import logging
import datetime
import random
from sqlalchemy import or_, desc, and_, func
from api.items.models import Item, ItemPhoto, Listing, ListingPhoto
from api.tags.models import Tag, Platform, Category, Subcategory, Color, Condition
from base import ApiHandler, die, paginate
from helpers import route, sa_object_to_dict
from utility.google_api import get_city_by_code
from utility.tags import interested_user_tag_ids, interested_user_item_ids

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('items')
class ItemsHandler(ApiHandler):
    allowed_methods = ('GET', 'POST', )

    def read(self):

        if not self.user:
            die(401)

        item_id = self.get_arg('item_id', int)
        q = self.get_arg('q', str)
        response = dict()

        # get item by id
        if item_id:
            # first get this item
            item = self.session.query(Item).filter(Item.id == item_id).first()
            if not item:
                return self.make_error('No item with id %s' % item_id)

            # find 6 items with similar category | platform | subcategory
            similar_items = self.session.query(Item).filter(and_(or_(Item.platform_id == item.platform_id,
                                                                     Item.category_id == item.category_id,
                                                                     Item.subcategory_id == item.subcategory_id),
                                                                 Item.id != item.id)).limit(6)
            # find 6 items of this user
            user_items = self.session.query(Item).filter(and_(Item.user_id == item.user_id,
                                                              Item.id != item.id)).limit(6)
            # current_item_response = item.item_response
            # current_item_response['user'] = item.user.user_response
            response['item'] = item.item_response
            response['similar_items'] = [i.item_response for i in similar_items]
            response['user_items'] = [i.item_response for i in user_items]
        # else return all items
        else:
            # TODO uncomment to return items by user interests
            # user_tags_set = interested_user_tag_ids(self)
            # item_ids = interested_user_item_ids(self, user_tags_set)
            # items = self.session.query(Item).filter(Item.id.in_(list(item_ids))).order_by(desc(Item.id))

            # TODO 2015-07-08 return all items
            items = self.session.query(Item).order_by(desc(Item.id))

            # search
            # if we have searching query we must filtered all items
            if q:
                # first we must get all items
                all_items = self.session.query(Item)

                # next get all tags names to search.
                # note! we can search only by platform name, category name and subcategory name
                tag_names_to_search = set()
                for i in items:
                    tag_names_to_search.add(i.platform.name.lower())
                    tag_names_to_search.add(i.category.name.lower())
                    tag_names_to_search.add(i.subcategory.name.lower())

                # this is set with suitable tag names
                right_tag_names = set()
                right_title_or_description_item_ids = set()

                # we search by every word in phrase
                # so separate query string by whitespace symbol
                q_list = q.lower().split(' ')

                # go through every query word and search it in tags and items titles/descriptions
                for q_word in q_list:

                    # search in every tag key by every query word
                    for key in tag_names_to_search:
                        if q_word in key:
                            right_tag_names.add(key)

                    # filter items then return items with matching title or description
                    right_title_or_description = [i.id for i in all_items.filter(or_(func.lower(Item.title).ilike(u'%{0}%'.format(q_word)),
                                                                                     func.lower(Item.description).ilike(u'%{0}%'.format(q_word))))]
                    if right_title_or_description:
                        for i in right_title_or_description:
                            right_title_or_description_item_ids.add(i)

                # next step - get right tags ids
                right_tag_ids = [t.id for t in self.session.query(Tag).filter(func.lower(Tag.name).in_(right_tag_names))]

                # select items by suitable tag name
                right_tag_item_ids = [i.id for i in all_items.filter(or_(Item.platform_id.in_(right_tag_ids),
                                                                         Item.category_id.in_(right_tag_ids),
                                                                         Item.subcategory_id.in_(right_tag_ids)))]

                # finally get all items which match search terms
                items = all_items.filter(Item.id.in_(list(set(right_tag_item_ids +
                                                              list(right_title_or_description_item_ids))))).order_by(desc(Item.id))


                # TODO optimize using this
                # filtered them by platform | category | subcategory | title | description
                # items = all_items.filter(or_(Item.platform.name.ilike(u'%{0}%'.format(q)),
                #                              Item.category.name.ilike(u'%{0}%'.format(q)),
                #                              Item.subcategory.name.ilike(u'%{0}%'.format(q)),
                #                              Item.title.ilike(u'%{0}%'.format(q)),
                #                              Item.description.ilike(u'%{0}%'.format(q))))
            # pagination
            page = self.get_arg('p', int, 1)
            page_size = self.get_arg('page_size', int, 100)
            paginator, items = paginate(items, page, page_size)
            if paginator['pages'] < page:
                items = []
            response['paginator'] = paginator
            response['items'] = [i.item_response for i in items]

        return self.success(response)

    def create(self):

        if self.user is None:
            die(401)

        # check selling ability
        # if not self.user.facebook_id:
        #     return self.make_error("Sorry, but you cannot sell on Hawkist until you have connected a Facebook account.")
        if not self.user.email_status:
            return self.make_error("Sorry, but you cannot sell on Hawkist until you have confirmed an email address.")

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

        if not shipping_price and not collection_only:
            empty_field_error.append('shipping price or collection only')

        if not photos:
            empty_field_error.append('photos')

        for photo in photos:
            if not photo:
                empty_field_error.append('photos')
                break

        if not post_code:
            empty_field_error.append('post code')

        if not city:
            logger.debug('NO CITY')
            if 'post code' not in empty_field_error:
                empty_field_error.append('post code')

        if empty_field_error:
            empty_fields = ', '.join(empty_field_error)
            response = {
                'status': 6,
                'message': 'You must select a %s in order to create a listing.' % empty_fields,
                'empty_fields': empty_fields
            }
            logger.debug(response)
            return response

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
            return self.make_error('No subcategory with id %s' % subcategory_id)

        # check is this nesting right
        platform_children_ids = [child.id for child in platform.children_tags]
        if category_id not in platform_children_ids:
            # hotfix for this build
            # start
            c_name = category.name.upper()
            p_name = ''
            p2_name = ''
            if category.parent_tag and category.parent_tag.name != 'platform':
                p_name = category.parent_tag.name.upper()
                if category.parent_tag.parent_tag and category.parent_tag.parent_tag.name != 'platform':
                    p2_name = category.parent_tag.parent_tag.name.upper()
            if p_name:
                if p2_name:
                    text = "Platform %s has no tag %s (%s > %s). Try again" % (platform.name.upper(), c_name,
                                                                                     p2_name, p_name)
                else:
                    text = "Platform %s has no tag %s (%s). Try again" % (platform.name.upper(), c_name, p_name)
            else:
                text = "Platform %s has no tag %s. Try again" % (platform.name.upper(), c_name)
            return self.make_error(text)
            # end
            # return self.make_error("Platform %s has no tag %s. Try again" % (platform.name.upper(),
            #                                                                        category.name.upper()))

        category_children_ids = [child.id for child in category.children_tags]
        if subcategory_id not in category_children_ids:
            # hotfix for this build
            # start
            c_name = subcategory.name.upper()
            p_name = ''
            p2_name = ''
            if subcategory.parent_tag and subcategory.parent_tag.name != 'platform':
                p_name = subcategory.parent_tag.name.upper()
                if subcategory.parent_tag.parent_tag and subcategory.parent_tag.parent_tag.name != 'platform':
                    p2_name = subcategory.parent_tag.parent_tag.name.upper()
            if p_name:
                if p2_name:
                    text = "Category %s has no tag %s (%s > %s). Try again" % (category.name.upper(), c_name,
                                                                                     p2_name, p_name)
                else:
                    text = "Category %s has no tag %s (%s). Try again" % (category.name.upper(), c_name, p_name)
            else:
                text = "Category %s has no tag %s. Try again" % (category.name.upper(), c_name)
            return self.make_error(text)
            # end
            # return self.make_error("Category %s has no tag %s. Try again" % (category.name.upper(),
            #                                                                        subcategory.name.upper()))

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
        retail_price = float(retail_price)
        selling_price = float(selling_price)
        shipping_price = float(shipping_price)
        if retail_price < 1:
            return self.make_error(u'Retail price must be greater than £1')

        if selling_price > retail_price or selling_price == retail_price:
                return self.make_error("Retail price must be greater than selling price")

        if shipping_price < 0:
            return self.make_error('Shipping price must be greater than or equal to £0')

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
            if discount == 0:
                discount = 1
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
            response = {
                'status': 6,
                'message': 'You must enter a post code in order to create a listing.'
            }
            logger.debug(response)
            return response

        google_response = get_city_by_code(post_code)
        error, data = google_response['error'], google_response['data']
        if error:
            logger.debug(error)
            return error
            # return self.make_error(error)
        return self.success({'city': data})


# TODO for listing edition
@route('listings')
class ListingHandler(ApiHandler):
    allowed_methods = ('GET', 'POST', )

    def read(self):

        if not self.user:
            die(401)

        listing_id = self.get_arg('item_id', int)
        q = self.get_arg('q', str)
        response = dict()

        # get item by id
        if listing_id:
            # first get this item
            listing = self.session.query(Listing).filter(Listing.id == listing_id).first()
            if not listing:
                return self.make_error('No item with id %s' % listing)

            # find 6 items with similar category | platform | subcategory
            similar_listings = self.session.query(Listing).filter(and_(or_(Listing.platform_id == listing.platform_id,
                                                                           Listing.category_id == listing.category_id,
                                                                           Listing.subcategory_id == listing.subcategory_id),
                                                                       Listing.id != listing.id)).limit(6)
            # find 6 items of this user
            user_listings = self.session.query(Listing).filter(and_(Listing.user_id == listing.user_id,
                                                                    Listing.id != listing.id)).limit(6)
            current_listing_response = listing.response
            current_listing_response['user'] = listing.user.user_response
            response['item'] = current_listing_response
            response['similar_items'] = [l.response for l in similar_listings]
            response['user_items'] = [l.response for l in user_listings]
        # else return all items
        else:
            # TODO uncomment to return items by user interests
            # get all user's tag
            user_tags = self.user.user_tags
            if not user_tags:
                logger.debug("User %s has no tags" % self.user.id)

            for u in user_tags:
                print u.id

            return
            user_tags_set = interested_user_tag_ids(self)
            # item_ids = interested_user_item_ids(self, user_tags_set)
            # items = self.session.query(Item).filter(Item.id.in_(list(item_ids))).order_by(desc(Item.id))

            # TODO 2015-07-08 return all items
            listings = self.session.query(Listing).order_by(desc(Listing.id))

            # search
            # if we have searching query we must filtered all items
            if q:
                # first we must get all items
                all_listings = self.session.query(Listing)

                # next get all tags names to search.
                # note! we can search only by platform name, category name and subcategory name
                tag_names_to_search = set()
                for i in all_listings:
                    tag_names_to_search.add(i.platform.title.lower())
                    tag_names_to_search.add(i.category.title.lower())
                    tag_names_to_search.add(i.subcategory.title.lower())

                # this is set with suitable tag names
                right_tag_names = set()
                right_title_or_description_item_ids = set()

                # we search by every word in phrase
                # so separate query string by whitespace symbol
                q_list = q.lower().split(' ')

                # go through every query word and search it in tags and items titles/descriptions
                for q_word in q_list:

                    # search in every tag key by every query word
                    for key in tag_names_to_search:
                        if q_word in key:
                            right_tag_names.add(key)

                    # filter items then return items with matching title or description
                    right_title_or_description = [i.id for i in all_listings.filter(or_(func.lower(Listing.title).ilike(u'%{0}%'.format(q_word)),
                                                                                        func.lower(Listing.description).ilike(u'%{0}%'.format(q_word))))]
                    if right_title_or_description:
                        for i in right_title_or_description:
                            right_title_or_description_item_ids.add(i)

                # next step - get right tags ids
                # right platforms
                right_platforms_ids = [p.id for p in self.session.query(Platform).filter(func.lower(Platform.title).in_(right_tag_names))]

                # right categories
                right_categories_ids = [c.id for c in self.session.query(Category).filter(func.lower(Category.title).in_(right_tag_names))]

                # right subcategories
                right_subcategories_ids = [s.id for s in self.session.query(Subcategory).filter(func.lower(Subcategory.title).in_(right_tag_names))]

                right_tag_ids = right_platforms_ids + right_categories_ids + right_subcategories_ids

                # select items by suitable tag name
                right_tag_item_ids = [i.id for i in all_listings.filter(or_(Item.platform_id.in_(right_tag_ids),
                                                                            Item.category_id.in_(right_tag_ids),
                                                                            Item.subcategory_id.in_(right_tag_ids)))]

                # finally get all items which match search terms
                listings = all_listings.filter(Listing.id.in_(list(set(right_tag_item_ids +
                                                                       list(right_title_or_description_item_ids))))).order_by(desc(Listing.id))


                # TODO optimize using this
                # filtered them by platform | category | subcategory | title | description
                # items = all_items.filter(or_(Item.platform.name.ilike(u'%{0}%'.format(q)),
                #                              Item.category.name.ilike(u'%{0}%'.format(q)),
                #                              Item.subcategory.name.ilike(u'%{0}%'.format(q)),
                #                              Item.title.ilike(u'%{0}%'.format(q)),
                #                              Item.description.ilike(u'%{0}%'.format(q))))
            # pagination
            page = self.get_arg('p', int, 1)
            page_size = self.get_arg('page_size', int, 100)
            paginator, items = paginate(listings, page, page_size)
            if paginator['pages'] < page:
                listings = []
            response['paginator'] = paginator
            response['items'] = [l.response for l in listings]

        return self.success(response)

    def create(self):

        if self.user is None:
            die(401)

        # check selling ability
        # if not self.user.facebook_id:
        #     return self.make_error("Sorry, but you cannot sell on Hawkist until you have confirmed an email address.")
        # if not self.user.email_status:
        #     return self.make_error("Sorry, but you cannot sell on Hawkist until you have connected a Facebook account.")

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
            empty_field_error.append('colour')

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
        platform = self.session.query(Platform).filter(Platform.id == platform_id).first()
        if not platform:
            return self.make_error('No platform with id %s' % platform_id)

        # check category
        category = self.session.query(Category).filter(Category.id == category_id).first()
        if not category:
            return self.make_error('No category with id %s' % category_id)

        # check subcategory
        subcategory = self.session.query(Subcategory).filter(Subcategory.id == subcategory_id).first()
        if not subcategory:
            return self.make_error('No subcategory with id %s' % category_id)

        # check color
        colour = self.session.query(Color).filter(Color.id == color_id).first()
        if not colour:
            return self.make_error('No color with id %s' % color_id)

        # check condition
        condition = self.session.query(Condition).filter(Condition.id == condition_id).first()
        if not condition:
            return self.make_error('No condition with id %s' % condition_id)

        # check is this nesting right
        platform_categories = [c.id for c in platform.category_platform]
        if category_id not in platform_categories:
            return self.make_error("Platform %s has no category %s (%s). Try again"
                                   % (platform.title.upper(), category.title.upper(), category.platform.title.upper()))

        category_subcategories = [c.id for c in category.subcategory_category]
        if subcategory_id not in category_subcategories:
            return self.make_error("Category %s (%s) has no subcategory %s (%s -> %s). Try again"
                                   % (category.title.upper(), category.platform.title.upper(),
                                      subcategory.title.upper(), subcategory.category.platform.title.upper(),
                                      subcategory.category.title.upper()))

        subcategory_color = [c.id for c in subcategory.color_subcategory]
        if color_id not in subcategory_color:
            return self.make_error("Subcategory %s (%s -> %s) has no color %s (%s -> %s -> %s). Try again"
                                   % (subcategory.title.upper(), subcategory.category.platform.title.upper(),
                                      subcategory.category.title.upper(), colour.title.upper(),
                                      colour.subcategory.category.platform.title.upper(),
                                      colour.subcategory.category.title.upper(),
                                      colour.subcategory.title.upper()))

        subcategory_condition = [c.id for c in subcategory.condition_subcategory]
        if condition_id not in subcategory_condition:
            return self.make_error("Subcategory %s (%s -> %s) has no condition %s (%s -> %s -> %s). Try again"
                                   % (subcategory.title.upper(), subcategory.category.platform.title.upper(),
                                      subcategory.category.title.upper(), condition.title.upper(),
                                      condition.subcategory.category.platform.title.upper(),
                                      condition.subcategory.category.title.upper(), condition.subcategory.title.upper()))

        # secondary check other fields
        # price handler
        if retail_price < 1:
            return self.make_error(u'Retail price must be greater than £1')

        if selling_price > retail_price:
            return self.make_error("Retail price must be greater than selling price")
                
        if shipping_price < 0:
            return self.make_error('Shipping price must be greater than or equal to £0')

        if len(photos) > 3:
            return self.make_error('You can add only 3 photos')

        # finally create listing
        listing = Listing()
        listing.user = self.user
        listing.created_at = datetime.datetime.utcnow()
        listing.updated_at = datetime.datetime.utcnow()
        listing.title = title
        listing.description = description

        if barcode:
            listing.barcode = barcode

        listing.platform_id = platform_id
        listing.category_id = category_id
        listing.subcategory_id = subcategory_id
        listing.condition_id = condition_id
        listing.color_id = color_id
        listing.retail_price = retail_price
        listing.selling_price = selling_price

        if selling_price != retail_price:
            # calculate discount value
            discount = int(round((retail_price - selling_price) / retail_price * 100))
            listing.discount = discount

        listing.shipping_price = shipping_price
        if collection_only:
            listing.collection_only = True
        else:
            listing.collection_only = False

        listing.post_code = post_code
        listing.city = city

        # self.session.flush(item)
        # self.session.commit()

        # photos
        for photo in photos:
            listing_photo = ListingPhoto()
            listing_photo.created_at = datetime.datetime.utcnow()
            listing_photo.listing = listing
            listing_photo.image_url = photo
            self.session.add(listing_photo)
            self.session.commit()

        self.session.commit()
        return self.success({'item': listing.response})
