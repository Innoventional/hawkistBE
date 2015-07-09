import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Boolean, Numeric
from sqlalchemy import Integer
from sqlalchemy.orm import relationship, backref
from api.users.models import User
from orm import Base

__author__ = 'ne_luboff'


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user = relationship(User, backref=backref('items', order_by=id, cascade="all,delete", lazy='dynamic'),
                        foreign_keys=user_id)

    title = Column(String, nullable=False, default='')
    description = Column(String, nullable=False, default='')
    barcode = Column(String, nullable=False, default='')

    # item details (tags)
    platform_id = Column(Integer, ForeignKey('tags.id'), nullable=False, index=True)
    platform = relationship('Tag', backref=backref('platform_items', order_by=id, cascade="all,delete", lazy='dynamic'),
                            foreign_keys=platform_id)

    category_id = Column(Integer, ForeignKey('tags.id'), nullable=False, index=True)
    category = relationship('Tag', backref=backref('category_items', order_by=id, cascade="all,delete", lazy='dynamic'),
                            foreign_keys=category_id)

    subcategory_id = Column(Integer, ForeignKey('tags.id'), nullable=False, index=True)
    subcategory = relationship('Tag', backref=backref('subcategory_items', order_by=id, cascade="all,delete",
                                                    lazy='dynamic'), foreign_keys=subcategory_id)

    condition_id = Column(Integer, ForeignKey('tags.id'), nullable=False, index=True)
    condition = relationship('Tag', backref=backref('condition_items', order_by=id, cascade="all,delete",
                                                  lazy='dynamic'), foreign_keys=condition_id)

    color_id = Column(Integer, ForeignKey('tags.id'), nullable=False, index=True)
    color = relationship('Tag', backref=backref('color_items', order_by=id, cascade="all,delete", lazy='dynamic'),
                         foreign_keys=color_id)

    # price
    retail_price = Column(Numeric, nullable=False)
    selling_price = Column(Numeric, nullable=True)
    discount = Column(Integer, nullable=True)

    shipping_price = Column(Numeric, nullable=True)
    collection_only = Column(Boolean, nullable=False, default=False)

    # location info info
    post_code = Column(String, nullable=True)
    city = Column(String, nullable=True)
    location_lat = Column(Numeric, nullable=True)
    location_lon = Column(Numeric, nullable=True)

    def __repr__(self):
        return '<Item %s (%s)>' % (self.id, self.title)

    @property
    def item_response(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_username': self.user.username,
            'user_avatar': self.user.avatar,
            'created_at': self.created_at,
            'title': self.title,
            'description': self.description,
            'platform': self.platform_id,
            'category': self.category_id,
            'subcategory': self.subcategory_id,
            'condition': self.condition_id,
            'color': self.color_id,
            'retail_price': self.retail_price,
            'selling_price': self.selling_price,
            'discount': self.discount,
            'shipping_price': self.shipping_price,
            'collection_only': self.collection_only,
            'post_code': self.post_code,
            'city': self.city,
            'photos': [photo.image_url for photo in self.item_photos],
        }


class ItemPhoto(Base):
    __tablename__ = 'item_photos'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    item_id = Column(Integer, ForeignKey('items.id'), nullable=False, index=True)
    item = relationship(Item, backref=backref('item_photos', order_by=id, cascade="all,delete", lazy='dynamic'),
                        foreign_keys=item_id)

    image_url = Column(String, nullable=False)


# TODO  new release


class Listing(Base):
    __tablename__ = 'listings'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user = relationship('User', backref=backref('listings', order_by=id, cascade="all,delete", lazy='dynamic'),
                        foreign_keys=user_id)

    title = Column(String, nullable=False, default='')
    description = Column(String, nullable=False, default='')
    barcode = Column(String, nullable=False, default='')

    # listing details (metatags)
    platform_id = Column(Integer, ForeignKey('platforms.id'), nullable=False, index=True)
    platform = relationship('Platform', backref=backref('platform_items', order_by=id, cascade="all,delete", lazy='dynamic'),
                            foreign_keys=platform_id)

    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False, index=True)
    category = relationship('Category', backref=backref('category_items', order_by=id, cascade="all,delete", lazy='dynamic'),
                            foreign_keys=category_id)

    subcategory_id = Column(Integer, ForeignKey('subcategories.id'), nullable=False, index=True)
    subcategory = relationship('Subcategory', backref=backref('subcategory_items', order_by=id, cascade="all,delete",
                                                              lazy='dynamic'), foreign_keys=subcategory_id)

    condition_id = Column(Integer, ForeignKey('conditions.id'), nullable=False, index=True)
    condition = relationship('Condition', backref=backref('condition_items', order_by=id, cascade="all,delete",
                                                          lazy='dynamic'), foreign_keys=condition_id)

    color_id = Column(Integer, ForeignKey('colors.id'), nullable=False, index=True)
    color = relationship('Color', backref=backref('color_items', order_by=id, cascade="all,delete", lazy='dynamic'),
                         foreign_keys=color_id)

    # price
    retail_price = Column(Numeric, nullable=False)
    selling_price = Column(Numeric, nullable=True)
    discount = Column(Integer, nullable=True)

    shipping_price = Column(Numeric, nullable=True)
    collection_only = Column(Boolean, nullable=False, default=False)

    # location info info
    post_code = Column(String, nullable=True)
    city = Column(String, nullable=True)
    location_lat = Column(Numeric, nullable=True)
    location_lon = Column(Numeric, nullable=True)

    def __repr__(self):
        return '<Item %s (%s)>' % (self.id, self.title)

    @property
    def response(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_username': self.user.username,
            'user_avatar': self.user.avatar,
            'created_at': self.created_at,
            'title': self.title,
            'description': self.description,
            'platform': self.platform_id,
            'category': self.category_id,
            'subcategory': self.subcategory_id,
            'condition': self.condition_id,
            'color': self.color_id,
            'retail_price': self.retail_price,
            'selling_price': self.selling_price,
            'discount': self.discount,
            'shipping_price': self.shipping_price,
            'collection_only': self.collection_only,
            'post_code': self.post_code,
            'city': self.city,
            'photos': [photo.image_url for photo in self.listing_photos],
        }


class ListingPhoto(Base):
    __tablename__ = 'listing_photos'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    listing_id = Column(Integer, ForeignKey('listings.id'), nullable=False, index=True)
    listing = relationship(Listing, backref=backref('listing_photos', order_by=id, cascade="all,delete", lazy='dynamic'),
                           foreign_keys=listing_id)

    image_url = Column(String, nullable=False)