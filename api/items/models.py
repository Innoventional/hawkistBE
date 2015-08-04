import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Boolean, Numeric, Table, Enum, SmallInteger
from sqlalchemy import Integer
from sqlalchemy.orm import relationship, backref
from orm import Base

__author__ = 'ne_luboff'


listing_likes = Table("listing_likes", Base.metadata,
                      Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
                      Column("listing_id", Integer, ForeignKey("listings.id"), primary_key=True),
                      Column("created_at", DateTime, nullable=False, default=datetime.datetime.utcnow))

listing_views = Table("listing_views", Base.metadata,
                      Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
                      Column("listing_id", Integer, ForeignKey("listings.id"), primary_key=True),
                      Column("created_at", DateTime, nullable=False, default=datetime.datetime.utcnow))


class ListingStatus(Enum):
    Active = 0
    Reserved = 1
    Sold = 2


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
    sold = Column(Boolean, nullable=False, default=False)
    status = Column(SmallInteger, nullable=True, default=ListingStatus.Active)

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

    likes = relationship('User', secondary=listing_likes, backref='likes')
    views = relationship('User', secondary=listing_views, backref='views')

    def __repr__(self):
        return '<Item %s (%s)>' % (self.id, self.title)

    def get_shipping_price_value(self):
        try:
            return "%.02f" % float(self.shipping_price)
        except:
            return self.shipping_price

    def get_comment_count(self, user_id):
        # so, we must go through every listing comment and check does current user can see it
        # first get all comments
        listing_comments = self.listing_comments
        listing_comment_count = 0
        if listing_comments:
            for comment in listing_comments:
                # check is this just comment of offer
                if comment.offer:
                    # check get current user access to this offer
                    if str(comment.offer.user_id) == str(user_id) \
                            or str(comment.offer.listing.user_id) == str(user_id):
                        listing_comment_count += 1
                else:
                    listing_comment_count += 1
        return listing_comment_count

    def response(self, user_id):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_username': self.user.username,
            'user_avatar': self.user.avatar,
            'created_at': self.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            'title': self.title,
            'description': self.description,
            'platform': self.platform_id,
            'category': self.category_id,
            'subcategory': self.subcategory_id,
            'condition': self.condition_id,
            'color': self.color_id,
            'retail_price': "%.02f" % float(self.retail_price),
            # 'retail_price': float(self.retail_price),
            'selling_price': "%.02f" % float(self.selling_price),
            # 'selling_price': float(self.selling_price),
            'discount': self.discount,
            'shipping_price': self.get_shipping_price_value(),
            'collection_only': self.collection_only,
            'post_code': self.post_code,
            'city': self.city,
            'photos': [photo.image_url for photo in self.listing_photos],
            'sold': self.sold,
            'status': self.status,
            'likes': len(self.likes),
            'views': len(self.views),
            'comments': self.get_comment_count(user_id)
        }


class ListingPhoto(Base):
    __tablename__ = 'listing_photos'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    listing_id = Column(Integer, ForeignKey('listings.id'), nullable=False, index=True)
    listing = relationship(Listing, backref=backref('listing_photos', order_by=id, cascade="all,delete", lazy='dynamic'),
                           foreign_keys=listing_id)

    image_url = Column(String, nullable=False)