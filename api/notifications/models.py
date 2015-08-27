import datetime
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, SmallInteger, Enum, Numeric
from sqlalchemy.orm import relationship, backref
from orm import Base

__author__ = 'ne_luboff'


class NotificationType(Enum):
    NewComment = 0
    ItemSold = 1
    ItemReceived = 2
    NewFeedback = 3
    FundsReleased = 4
    LeaveFeedback = 5
    ItemIsFavourited = 6
    AFavouriteItemIsSold = 7
    NewFollowers = 8
    NewItems = 9
    Mentions = 10
    NewOfferedPrice = 11
    OfferedPriceAccepted = 12
    OfferedPriceDeclined = 13


class NotificationPriority(Enum):
    High = 0
    Low = 1
    Mandatory = 2


class UserNotificantion(Base):
    __tablename__ = 'user_notifications'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    seen_at = Column(DateTime, nullable=True)
    response_time = Column(Integer, default=0, nullable=False)

    # reference to user-owner
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner = relationship('User', backref=backref('user_notifications', order_by=id, cascade="all,delete",
                                                 lazy='dynamic'), foreign_keys=owner_id)

    type = Column(SmallInteger, nullable=False, default=NotificationType.NewComment)
    priority = Column(SmallInteger, nullable=False, default=NotificationPriority.Low)

    # info about user
    user_id = Column(Integer, nullable=True)
    user_username = Column(String, nullable=True)
    user_avatar = Column(String, nullable=True)

    # info about listing
    listing_id = Column(Integer, nullable=True)
    listing_title = Column(String, nullable=True)
    listing_photo = Column(String, nullable=True)
    listing_selling_price = Column(Numeric, nullable=True)
    listing_shipping_price = Column(Numeric, nullable=True)

    # info about comment
    comment_id = Column(Integer, nullable=True)
    comment_text = Column(String, nullable=True)
    comment_offer_price = Column(Numeric, nullable=True)

    # info about order
    order_id = Column(Integer, nullable=True)

    def get_shipping_price_value(self):
        try:
            return "%.02f" % float(self.listing_shipping_price)
        except:
            return self.listing_shipping_price

    @property
    def response(self):
        return {
            'id': self.id,
            'type': self.type,
            'created_at': self.created_at.strftime("%Y-%m-%dT%H:%M"),
            'user': {
                'id': self.user_id,
                'username': self.user_username,
                'avatar': self.user_avatar
            },
            'listing': {
                'id': self.listing_id,
                'selling_price': "%.02f" % float(self.listing_selling_price) if self.listing_selling_price else None,
                'shipping_price': self.get_shipping_price_value(),
                'photo': self.listing_photo,
                'title': self.listing_title
            },
            'comment': {
                'text': self.comment_text,
                'offered_price': "%.02f" % float(self.comment_offer_price) if self.comment_offer_price else None
            },
            'order': {
                'id': self.order_id,
            }
        }