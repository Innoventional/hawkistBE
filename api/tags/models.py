import datetime
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from orm import Base

__author__ = 'ne_luboff'


class Tag(Base):
    __tablename__ = 'tags'
    __json_extra__ = ('tag_response')

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    name = Column(String, nullable=False, default='')
    parent_tag_id = Column(Integer, ForeignKey('tags.id'), nullable=True, index=True)
    parent_tag = relationship('Tag', remote_side=[id], backref=backref('children_tags', order_by=id,
                                                                       cascade="all,delete", lazy='dynamic'),
                              foreign_keys=parent_tag_id)

    @property
    def tag_response(self):
        return {
            'id': self.id,
            'name': self.name,
            # 'parent_tag_id': self.parent_tag_id or ''
        }