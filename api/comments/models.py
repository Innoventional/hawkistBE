import datetime
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Table
from sqlalchemy.orm import backref, relationship
from orm import Base

__author__ = 'ne_luboff'

comment_mentioned_users = Table("comment_mentioned_users", Base.metadata,
                                Column("comment_id", Integer, ForeignKey("comments.id"), primary_key=True),
                                Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
                                Column("created_at", DateTime, nullable=False, default=datetime.datetime.utcnow))


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

    offer_id = Column(Integer, ForeignKey('offers.id'), nullable=True, index=True)
    offer = relationship('Offer', backref=backref('offer_comment', order_by=id, cascade="all,delete",
                                                  lazy='dynamic'), foreign_keys=offer_id)

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
            'offer': self.offer.response if self.offer else None
        }
