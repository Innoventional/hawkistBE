import datetime
import re
from sqlalchemy import Column, Integer, DateTime, ForeignKey, SmallInteger, Enum
from sqlalchemy.orm import relationship, backref
from orm import Base

__author__ = 'ne_luboff'


class ListingReportingReasons(Enum):
    ItemViolatesTermsOfUse = 0
    ItemIsStolenOrCounterfeit = 1
    ItemIsRegulatedOrIllegal = 2

    @classmethod
    def tostring(cls, val):
        for k, v in vars(cls).iteritems():
            if v == val:
                return ' '.join([a for a in re.split(r'([A-Z][a-z]*)', k) if a])


class ReportedListings(Base):
    __tablename__ = 'reported_listings'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user = relationship('User', backref=backref('reported_listings', order_by=id, cascade="all,delete", lazy='dynamic'),
                        foreign_keys=user_id)

    listing_id = Column(Integer, ForeignKey('listings.id'), nullable=False, index=True)
    listing = relationship('Listing', backref=backref('reports', order_by=id, cascade="all,delete", lazy='dynamic'),
                           foreign_keys=listing_id)

    reason = Column(SmallInteger, nullable=True, default=ListingReportingReasons.ItemViolatesTermsOfUse)
