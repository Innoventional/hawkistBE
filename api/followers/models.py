import datetime
from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime
from orm import Base

__author__ = 'ne_luboff'

user_followers = Table("user_followers", Base.metadata,
                       Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
                       Column("following_user_id", Integer, ForeignKey("users.id"), primary_key=True),
                       Column("created_at", DateTime, nullable=False, default=datetime.datetime.utcnow))
