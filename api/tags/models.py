import datetime
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, SmallInteger, Enum
from sqlalchemy.orm import relationship, backref
from orm import Base

__author__ = 'ne_luboff'


class MetatagChildType(Enum):
    Subcategory = 0
    Color = 1
    Condition = 2

    @classmethod
    def tostring(cls, val):
        for k, v in vars(cls).iteritems():
            if v == val:
                return k


class Tag(Base):
    __tablename__ = 'tags'
    __json_extra__ = ('tag_response')

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    name = Column(String, nullable=False, default='')
    parent_tag_id = Column(Integer, ForeignKey('tags.id'), nullable=True, index=True)
    parent_tag = relationship('Tag', remote_side=[id], backref=backref('children_tags', order_by=id,
                                                                       cascade="all,delete", lazy='dynamic'),
                              foreign_keys=parent_tag_id)

    @property
    def tag_response(self):
        return {
            'id': self.id,
            'name': self.name,
            # 'parent_tag_id': self.parent_tag_id or ''
        }


class Platform(Base):
    __tablename__ = 'platforms'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    title = Column(String, nullable=False, default='')

    @property
    def response(self):
        return {
            'id': self.id,
            'name': self.title,
            'parent_id': None
        }


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    title = Column(String, nullable=False, default='')

    # depends on platform
    platform_id = Column(Integer, ForeignKey('platforms.id'), nullable=False, index=True)
    platform = relationship('Platform', backref=backref('category_platform', order_by=id, cascade="all,delete",
                                                        lazy='dynamic'), foreign_keys=platform_id)

    @property
    def response(self):
        return {
            'id': self.id,
            'name': self.title,
            'parent_id': self.platform_id
        }


class Subcategory(Base):
    __tablename__ = 'subcategories'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    title = Column(String, nullable=False, default='')

    # depends on category
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False, index=True)
    category = relationship('Category', backref=backref('subcategory_category', order_by=id, cascade="all,delete",
                                                        lazy='dynamic'), foreign_keys=category_id)

    @property
    def response(self):
        return {
            'id': self.id,
            'name': self.title,
            'parent_id': self.category_id
        }


class Color(Base):
    __tablename__ = 'colors'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    title = Column(String, nullable=False, default='')
    code = Column(String, nullable=True, default='')

    # depends on subcategory
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'), nullable=False, index=True)
    subcategory = relationship('Subcategory', backref=backref('color_subcategory', order_by=id, cascade="all,delete",
                                                              lazy='dynamic'), foreign_keys=subcategory_id)

    @property
    def response(self):
        return {
            'id': self.id,
            'name': self.title,
            'rgb_code': self.code,
            'parent_id': self.subcategory_id
        }


class Condition(Base):
    __tablename__ = 'conditions'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    title = Column(String, nullable=False, default='')

    # depends on subcategory
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'), nullable=False, index=True)
    subcategory = relationship('Subcategory', backref=backref('condition_subcategory', order_by=id, cascade="all,delete",
                                                              lazy='dynamic'), foreign_keys=subcategory_id)

    @property
    def response(self):
        return {
            'id': self.id,
            'name': self.title,
            'parent_id': self.subcategory_id
        }