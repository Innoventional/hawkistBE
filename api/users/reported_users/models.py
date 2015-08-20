import datetime
import re
from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime, Enum
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


user_reportlist = Table("user_reportlist", Base.metadata,
                        Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
                        Column("reported_user_id", Integer, ForeignKey("users.id"), primary_key=True),
                        Column("reason", Integer, nullable=False, default=UserReportingReasons.AbusiveBehaviour),
                        Column("created_at", DateTime, nullable=False, default=datetime.datetime.utcnow))
