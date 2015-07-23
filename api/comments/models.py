import datetime
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import backref, relationship
from orm import Base

__author__ = 'ne_luboff'


# comments for listings
class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    text = Column(String, nullable=True, default='')

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user = relationship('User', backref=backref('user_comments', order_by=id, cascade="all,delete", lazy='dynamic'),
                        foreign_keys=user_id)

    listing_id = Column(Integer, ForeignKey('listings.id'), nullable=False, index=True)
    listing = relationship('Listing', backref=backref('listing_comments', order_by=id, cascade="all,delete",
                                                      lazy='dynamic'), foreign_keys=listing_id)

    user_to_see_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    user_to_see = relationship('User', backref=backref('user_specific_comments', order_by=id, cascade="all,delete",
                                                       lazy='dynamic'), foreign_keys=user_to_see_id)

    @property
    def response(self):
        return {
            'id': self.id,
            'created_at': self.created_at.strftime("%Y-%m-%dT%H:%M"),
            'text': self.text,
            'listing_id': self.listing_id,
            'user_id': self.user_id,
            'user_username': self.user.username,
            'user_avatar': self.user.avatar,
            'offered_user': self.user_to_see_id
        }
