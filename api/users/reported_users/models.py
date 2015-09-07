import datetime
import re
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, SmallInteger
from sqlalchemy.orm import relationship, backref
from orm import Base

__author__ = 'ne_luboff'


class UserReportingReasons(Enum):
    AbusiveBehaviour = 0
    InappropriateContent = 1
    ImpersonationOrHateAccount = 2
    SellingFakeItems = 3
    UnderagedAccount = 4

    @classmethod
    def tostring(cls, val):
        for k, v in vars(cls).iteritems():
            if v == val:
                return ' '.join([a for a in re.split(r'([A-Z][a-z]*)', k) if a])


class ReportedUsers(Base):
    __tablename__ = 'reported_users'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user = relationship('User', backref=backref('reported_users', order_by=id, cascade="all,delete", lazy='dynamic'),
                        foreign_keys=user_id)

    reported_user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    reported_user = relationship('User', backref=backref('reported_me_users', order_by=id, cascade="all,delete",
                                                         lazy='dynamic'), foreign_keys=reported_user_id)

    reason = Column(SmallInteger, nullable=True, default=UserReportingReasons.AbusiveBehaviour)


# user_reportlist = Table("user_reportlist", Base.metadata,
#                         Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
#                         Column("reported_user_id", Integer, ForeignKey("users.id"), primary_key=True),
#                         Column("reason", Integer, nullable=False, default=UserReportingReasons.AbusiveBehaviour),
#                         Column("created_at", DateTime, nullable=False, default=datetime.datetime.utcnow))
