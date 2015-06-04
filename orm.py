from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import MetaData
from environment import env


engine = create_engine(env['db'], pool_timeout=60, client_encoding='utf8')
Base = declarative_base(engine)
metadata = MetaData(engine)


def create_session(scopefunc=None):
    return scoped_session(sessionmaker(bind=engine), scopefunc=scopefunc)


class new_session(object):
    def __init__(self):
        self.session = create_session(self.__enter__)

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.remove()
