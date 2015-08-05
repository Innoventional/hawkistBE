import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, SmallInteger, Enum
from sqlalchemy.orm import relationship, backref
from orm import Base

__author__ = 'ne_luboff'


class OrderStatus(Enum):
    """
    Active - listing purchase process started;
    Received - buyer received listing and send money to seller;
    HasAnIssue - some problem with listing (see IssueReason enum class).
    """
    Active = 0
    Received = 1
    HasAnIssue = 2


class IssueReason(Enum):
    """
    Reasons why user want to decline listing
    """
    ItemHasNotArrived = 0
    ItemIsNotAsDescribed = 1
    ItemIsBrokenOrNotUsable = 2


class IssueStatus(Enum):
    """
    Active - issue not in processing;
    Investigating - issue open by admin/support/developer;
    Cancelled - start refund money to buyer;
    RefundIssued - automatically appears then money refunded;
    Resolved - send money to seller.
    """
    Active = 0
    Investigating = 1
    Cancelled = 2
    RefundIssued = 3
    Resolved = 4


class UserOrders(Base):
    __tablename__ = 'user_orders'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)

    # reference to user
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user = relationship('User', backref=backref('user_orders', order_by=id, cascade="all,delete", lazy='dynamic'),
                        foreign_keys=user_id)

    # reference to bought listing
    listing_id = Column(Integer, ForeignKey('listings.id'), nullable=True)
    listing = relationship('Listing', backref=backref('bought', order_by=id, cascade="all,delete",
                                                      lazy='dynamic'), foreign_keys=listing_id)

    # reference to charge
    charge_id = Column(Integer, ForeignKey('stripe_charges.id'), nullable=True)
    charge = relationship('StripeCharges', backref=backref('order_charge', order_by=id, cascade="all,delete",
                                                           lazy='dynamic'), foreign_keys=charge_id)

    # primary order status
    order_status = Column(SmallInteger, nullable=False, default=OrderStatus.Active)

    # if this listing has an issue
    issue_reason = Column(SmallInteger, nullable=True)
    issue_status = Column(SmallInteger, nullable=True, default=IssueStatus.Active)

    @property
    def response(self):
        return {
            'id': self.id,
            'listing': {
                'id': self.listing.id,
                'title': self.listing.title,
                'image': self.listing.listing_photos[0].image_url,
                'retail_price': "%.02f" % float(self.listing.retail_price),
                'selling_price': "%.02f" % float(self.listing.selling_price),
            },
            'status': self.order_status
        }
