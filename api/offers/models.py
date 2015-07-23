import datetime
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Numeric, SmallInteger, Enum
from sqlalchemy.orm import backref, relationship
from orm import Base

__author__ = 'ne_luboff'


# offers statuses enum
class OfferStatus(Enum):
    Active = 0
    Accepted = 1
    Declined = 2

    @classmethod
    def tostring(cls, val):
        for k, v in vars(cls).iteritems():
            if v == val:
                return k


# offers for listings
class Offer(Base):
    __tablename__ = 'offers'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    new_price = Column(Numeric, nullable=False)
    status = Column(SmallInteger, nullable=False, default=OfferStatus.Active)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user = relationship('User', backref=backref('user_offers', order_by=id, cascade="all,delete", lazy='dynamic'),
                        foreign_keys=user_id)

    listing_id = Column(Integer, ForeignKey('listings.id'), nullable=False, index=True)
    listing = relationship('Listing', backref=backref('listing_offers', order_by=id, cascade="all,delete",
                                                      lazy='dynamic'), foreign_keys=listing_id)

    @property
    def response(self):
        return {
            'id': self.id,
            'status': self.status,
            'offer_receiver_id': self.listing.user_id,
            'offer_creater_id': self.user_id
        }
