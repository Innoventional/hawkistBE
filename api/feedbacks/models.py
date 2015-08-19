import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, SmallInteger, Enum
from sqlalchemy.orm import relationship, backref
from orm import Base

__author__ = 'ne_luboff'


class FeedbackType(Enum):
    Positive = 0
    Negative = 1
    Neutral = 2


class Feedback(Base):
    __tablename__ = 'user_feedbacks'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user = relationship('User', backref=backref('leaved_feedbacks', order_by=id, cascade="all,delete", lazy='dynamic'),
                        foreign_keys=user_id)

    to_user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    to_user = relationship('User', backref=backref('feedbacks', order_by=id, cascade="all,delete", lazy='dynamic'),
                           foreign_keys=to_user_id)

    text = Column(String, nullable=True)
    type = Column(SmallInteger, nullable=True, default=FeedbackType.Neutral)

    @property
    def response(self):
        return {
            'id': self.id,
            'text': self.text,
            'created_at': self.created_at,
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'avatar': self.user.avatar
            }
        }