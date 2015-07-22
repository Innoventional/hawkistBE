import datetime
from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from orm import Base

__author__ = 'ne_luboff'

user_blacklist = Table("user_blacklist", Base.metadata,
                       Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
                       Column("blocked_user_id", Integer, ForeignKey("users.id"), primary_key=True),
                       Column("created_at", DateTime, nullable=False, default=datetime.datetime.utcnow))
