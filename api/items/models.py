import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Enum, SmallInteger, Boolean, Numeric
from sqlalchemy import Integer
from sqlalchemy.orm import relationship, backref
from api.users.models import User
from orm import Base

__author__ = 'ne_luboff'


class ItemCondition(Enum):
    BrandNewInBox = 0
    LikeNew = 1
    Used = 2
    Refurbished = 3
    NotWorkingOrPartsOnly = 4


class ItemColor(Enum):
    Black = 0
    White = 1
    Red = 2
    Blue = 3
    Green = 4
    Orange = 5
    Yellow = 6
    Purple = 7
    Other = 8
    NotApplicable = 9


class ItemPlatform(Enum):
    PC = 0
    MAC = 1
    Playstation = 2
    XBOX = 3
    Nintendo = 4
    Sega = 5


class ItemCategory(Enum):
    Consoles = 0
    Games = 1
    Handhelp = 2
    Accessories = 3


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
    platform = Column(SmallInteger, nullable=False)
    category = Column(SmallInteger, nullable=False)
    condition = Column(SmallInteger, nullable=False)
    color = Column(String, nullable=False)

    # price
    retail_price = Column(Integer, nullable=False)
    selling_price = Column(Integer, nullable=False)
    discount = Column(Integer, nullable=True)

    shipping_price = Column(Integer, nullable=True)
    collection_only = Column(Boolean, nullable=False, default=False)

    # location info info
    post_code = Column(Integer, nullable=True)
    city = Column(String, nullable=True)
    location_lat = Column(Numeric, nullable=True)
    location_lon = Column(Numeric, nullable=True)

    def __repr__(self):
        return '<Item %s (%s)>' % (self.id, self.title)

    @property
    def item_response(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'title': self.title,
            'description': self.description,
            'platform': self.platform,
            'category': self.category,
            'condition': self.condition,
            'color': self.color,
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