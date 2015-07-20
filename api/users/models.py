import datetime
from sqlalchemy import Column, Integer, DateTime, String, Boolean, SmallInteger, ForeignKey, Enum
from sqlalchemy.orm import relationship, backref
from api.followers.models import user_followers
from api.tags.models import Tag
from api.users.blocked_users.models import user_blacklist
from api.users.reported_users.models import user_reportlist
from orm import Base

__author__ = 'ne_luboff'


class UserType(Enum):
    __order__ = '0 1 2 3'

    Admin = 0
    Developer = 1
    Support = 2
    Standard = 3

    @classmethod
    def tostring(cls, val):
        for k, v in vars(cls).iteritems():
            if v == val:
                return k


class SystemStatus(Enum):
    Active = 0
    Suspended = 1

    @classmethod
    def tostring(cls, val):
        for k, v in vars(cls).iteritems():
            if v == val:
                return k


class User(Base):
    __tablename__ = 'users'
    __json_extra__ = ('user_response')

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    # if user sign up via phone
    phone = Column(String(20), nullable=True, default='')
    pin = Column(String, nullable=True, default='')
    last_pin_sending = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)
    sent_pins_count = Column(SmallInteger, nullable=True, default=0)

    # if user use fb
    facebook_id = Column(String, nullable=True, default='')

    username = Column(String, nullable=True, default='')
    email = Column(String, nullable=True, default='')
    info = Column(String, nullable=True, default='')
    avatar = Column(String, nullable=True, default='')
    thumbnail = Column(String, nullable=True, default='')

    # email must be verified for sales
    # TODO first email status is False
    email_status = Column(Boolean, nullable=False, default=False)
    email_salt = Column(String, nullable=True, default='')

    first_login = Column(Boolean, nullable=False, default=False)

    system_status = Column(SmallInteger, nullable=False, default=SystemStatus.Active)
    user_type = Column(SmallInteger, nullable=False, default=UserType.Standard)
    password = Column(String, nullable=True, default='')

    city = Column(String, nullable=True, default='')
    last_activity = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)

    following = relationship('User',
                             secondary=user_followers,
                             primaryjoin=id == user_followers.c.user_id,
                             secondaryjoin=id == user_followers.c.following_user_id)

    followers = relationship('User',
                             secondary=user_followers,
                             primaryjoin=id == user_followers.c.following_user_id,
                             secondaryjoin=id == user_followers.c.user_id)

    blocked = relationship('User',
                           secondary=user_blacklist,
                           primaryjoin=id == user_blacklist.c.user_id,
                           secondaryjoin=id == user_blacklist.c.blocked_user_id)

    reported = relationship('User',
                            secondary=user_reportlist,
                            primaryjoin=id == user_reportlist.c.user_id,
                            secondaryjoin=id == user_reportlist.c.reported_user_id)

    def __repr__(self):
        return '<User %s (%s)>' % (self.id, self.username)

    def get_user_tags(self):
        return [
            {
                "id": tag.tag.id,
                "name": tag.tag.name}
            for tag in self.user_tags
        ]

    def get_user_metatags(self):
        response = []
        user_metatags = self.user_metatags
        for m in user_metatags:
            current_tag_response = {
                'id': m.id,
                'type': m.metatag_type
            }
            # we must define type
            if m.metatag_type == 0:
                current_tag_response['metatag_id'] = m.platform.id
                current_tag_response['metatag_title'] = m.platform.title
            elif m.metatag_type == 1:
                current_tag_response['metatag_id'] = m.category.id
                current_tag_response['metatag_title'] = m.category.title
            elif m.metatag_type == 2:
                current_tag_response['metatag_id'] = m.subcategory.id
                current_tag_response['metatag_title'] = m.subcategory.title
            response.append(current_tag_response)
        return response

    def get_user_sales(self):
        user_listings = self.listings
        sold_user_listings = []
        for l in user_listings:
            if l.sold:
                sold_user_listings.append(l)
        return len(sold_user_listings)

    @property
    def user_response(self):
        return {
            'id': self.id,
            'avatar': self.avatar,
            'thumbnail': self.thumbnail,
            'username': self.username,
            'email': self.email,
            'about_me': self.info,
            'phone': self.phone,
            'facebook_id': self.facebook_id,
            'email_status': self.email_status,
            'first_login': self.first_login,
            'metatags': self.get_user_metatags(),
            'user_type': self.user_type,
            'system_status': self.system_status,
            'city': self.city,
            'last_activity': self.last_activity.strftime("%Y-%m-%dT%H:%M"),
            'number_of_sales': self.get_user_sales(),
            'rating': 4,
            'review': 17,
            'response_time': 5,
        }

    @property
    def following_response(self):
        return {
            'id': self.id,
            'avatar': self.avatar,
            'username': self.username,
            'rating': 4,
            'review': 17,
        }


class UserTags(Base):
    __tablename__ = 'users_tags'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user = relationship(User, backref=backref('user_tags', order_by=id, cascade="all,delete", lazy='dynamic'),
                        foreign_keys=user_id)
    tag_id = Column(Integer, ForeignKey('tags.id'), nullable=False, index=True)
    tag = relationship(Tag, backref=backref('tag_users', order_by=id, cascade="all,delete", lazy='dynamic'),
                       foreign_keys=tag_id)


class UserMetaTagType(Enum):
    Platform = 0
    Category = 1
    Subcategory = 2


class UserMetaTag(Base):
    __tablename__ = 'users_metatags'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user = relationship('User', backref=backref('user_metatags', order_by=id, cascade="all,delete", lazy='dynamic'),
                        foreign_keys=user_id)

    # selected metatags for user feeds can be 3 types: platform, category and subcategory
    metatag_type = Column(SmallInteger, nullable=False)
    platform_id = Column(Integer, ForeignKey('platforms.id'), nullable=True, index=True)
    platform = relationship('Platform', backref=backref('user_interested_platforms', order_by=id, cascade="all,delete",
                                                        lazy='dynamic'), foreign_keys=platform_id)

    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True, index=True)
    category = relationship('Category', backref=backref('user_interested_categories', order_by=id, cascade="all,delete",
                                                        lazy='dynamic'), foreign_keys=category_id)

    subcategory_id = Column(Integer, ForeignKey('subcategories.id'), nullable=True, index=True)
    subcategory = relationship('Subcategory', backref=backref('user_interested_subcategories', order_by=id,
                                                              cascade="all,delete", lazy='dynamic'), foreign_keys=subcategory_id)