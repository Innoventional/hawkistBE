import datetime
from sqlalchemy import Column, Integer, DateTime, String, Boolean, SmallInteger, ForeignKey, Enum
from sqlalchemy.orm import relationship, backref
from api.tags.models import Tag
from orm import Base

__author__ = 'ne_luboff'


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

    def __repr__(self):
        return '<User %s (%s)>' % (self.id, self.username)

    def get_user_tags(self):
        return [
            {
                "id": tag.tag.id,
                "name": tag.tag.name}
            for tag in self.user_tags
        ]

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
            'tags': self.get_user_tags()
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