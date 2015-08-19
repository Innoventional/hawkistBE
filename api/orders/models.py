import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, SmallInteger, Enum, Boolean
from sqlalchemy.orm import relationship, backref
from orm import Base
from utility.send_email import send_warning_3_5_days_email, funds_received_seller

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
    New = 0
    Investigating = 1
    Cancelled = 2
    RefundIssued = 3
    Resolved = 4

    @classmethod
    def tostring(cls, val):
        for k, v in vars(cls).iteritems():
            if v == val:
                return k


class UserOrders(Base):
    __tablename__ = 'user_orders'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)


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
    issue_status = Column(SmallInteger, nullable=True, default=IssueStatus.New)

    # reference to user
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user = relationship('User', backref=backref('user_orders', order_by=order_status, cascade="all,delete",
                                                lazy='dynamic'), foreign_keys=user_id)

    available_feedback = Column(Boolean, nullable=False, default=False)

    @property
    def response(self):
        return {
            'id': self.id,
            # 'listing': {
            #     'id': self.listing.id,
            #     'title': self.listing.title,
            #     'image': self.listing.listing_photos[0].image_url,
            #     'retail_price': "%.02f" % float(self.listing.retail_price),
            #     'selling_price': "%.02f" % float(self.listing.selling_price),
            # },
            'listing': self.listing.response(self.user_id),
            'status': self.order_status,
            'available_feedback': self.available_feedback
        }

    def warning_3_5_days(self):
        send_warning_3_5_days_email(self.email_user_email, self.email_user_username, self.email_listing_title)

    def automatic_money_release(self):
        funds_received_seller(self)
