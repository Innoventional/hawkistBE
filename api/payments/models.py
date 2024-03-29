# -*- coding: utf-8 -*-
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


class StripeCharges(Base):
    __tablename__ = 'stripe_charges'

    id = Column(Integer, autoincrement=True, primary_key=True)
    created_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, default=datetime.datetime.utcnow)

    charge_id = Column(String, nullable=False)
    transaction_id = Column(String, nullable=True)
    paid = Column(Boolean, default=False)
    refunded = Column(Boolean, default=False)
    payment_sum = Column(Numeric, nullable=True)
    transaction_status = Column(String, default="failed")

    buyer_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    buyer = relationship('User', backref=backref('user_charges', order_by=id, cascade="all,delete", lazy='dynamic'),
                         foreign_keys=buyer_id)

    listing_id = Column(Integer, ForeignKey('listings.id'), nullable=True, index=True)
    listing = relationship('Listing', backref=backref('listing_charges', order_by=id, cascade="all,delete",
                                                      lazy='dynamic'), foreign_keys=listing_id)