import datetime
from sqlalchemy import Column, DateTime, Integer, ForeignKey, String, Numeric, SmallInteger, Enum, Boolean
from sqlalchemy.orm import relationship, backref
from orm import Base

__author__ = 'ne_luboff'


# stripe customer
class StripeCustomer(Base):
    __tablename__ = 'stripe_customers'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)

    stripe_customer_id = Column(String, nullable=True)
    stripe_card_id = Column(String, nullable=True)


# TODO if we need to save card info
# bank cards model
# class Card(Base):
#     __tablename__ = 'cards'
#
#     id = Column(Integer, primary_key=True)
#     created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
#     updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
#
#     # card owner
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
#     user = relationship('User', backref=backref('user_cards', order_by=id, cascade="all,delete", lazy='dynamic'),
#                         foreign_keys=user_id)
#
#     # card info
#     name = Column(String, nullable=True)
#     number = Column(String(16), nullable=False)
#     cvv = Column(String, nullable=False)
#     exp_month = Column(Integer, nullable=False)
#     exp_year = Column(Integer, nullable=False)
#     address_line1 = Column(String, nullable=True)
#     address_line2 = Column(String, nullable=True)
#     address_city = Column(String, nullable=True)
#     address_postcode = Column(String, nullable=True)
#
#     # ref to stripe customer
#     stripe_customer_id = Column(Integer, ForeignKey('stripe_customers.id'), nullable=False, index=True)
#     stripe_customer = relationship('StripeCustomer', backref=backref('stripe_account', order_by=id,
#                                                                      cascade="all,delete", lazy='dynamic'),
#                                    foreign_keys=stripe_customer_id)
#
#     @property
#     def response(self):
#         return {
#             'id': self.id,
#             'name': self.name,
#             'number': self.number[:4],
#             'exp_month': self.exp_month,
#             'exp_year': self.exp_year
#         }


# available charges statuses
class ChargesStatus(Enum):
    Active = 0
    Frozen = 1
    Finished = 2


class ChargesTransactionStatus(Enum):
    Succeeded = 0
    Failed = 1


# stripe charges
# class StripeCharges(Base):
#     __tablename__ = 'stripe_charges'
#
#     id = Column(Integer, primary_key=True)
#     created_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)
#     updated_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)
#     date_start = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)
#     date_finish = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)
#     system_status = Column(SmallInteger, nullable=False, default=ChargesStatus.Active)
#
#     payment_sum = Column(Numeric, nullable=True)
#     payment_currency = Column(String(3), nullable=False)
#     charge_id = Column(String, nullable=True)
#     transaction_id = Column(String, nullable=True)
#     paid = Column(Boolean, default=False)
#     transaction_status = Column(String, default=ChargesTransactionStatus.Failed)
#     refunded = Column(Boolean, default=False)
#
#     buyer_stripe_card_id = Column(String, nullable=True)
#     buyer_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
#     buyer = relationship('User', backref=backref('buyer', order_by=id, cascade="all,delete", lazy='dynamic'),
#                          foreign_keys=buyer_id)
#
#     seller_stripe_card_id = Column(String, nullable=True)
#     seller_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
#     seller = relationship('User', backref=backref('seller', order_by=id, cascade="all,delete", lazy='dynamic'),
#                           foreign_keys=seller_id)
#
#     listing_id = Column(Integer, ForeignKey('listings.id'), nullable=False, index=True)
#     listing = relationship('Listing', backref=backref('listing_charges', order_by=id, cascade="all,delete",
#                                                       lazy='dynamic'), foreign_keys=listing_id)
