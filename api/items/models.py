import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String
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

    title = Column(String, nullable=True, default='')
    description = Column(String, nullable=True, default='')
    condition = Column(String, nullable=True, default='')
    color = Column(String, nullable=True, default='')
    barcode = Column(String, nullable=True, default='')


class ItemPhoto(Base):
    __tablename__ = 'item_photos'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    item_id = Column(Integer, ForeignKey('items.id'), nullable=False, index=True)
    item = relationship(Item, backref=backref('item_photos', order_by=id, cascade="all,delete", lazy='dynamic'),
                        foreign_keys=item_id)

    image_url = Column(String, nullable=False)