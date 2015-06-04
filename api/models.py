__author__ = 'ne_luboff'

from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String
from orm import Base
import logging


logger = logging.getLogger(__name__)


class ApiKey(Base):
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True)
    api_key = Column(String(100), nullable=False)
    api_pass = Column(String(100), nullable=False)

    def __repr__(self):
        return '<ApiKey %s, %s>' % (self.api_key, self.api_pass)
