import logging
import datetime
from base import OpenApiHandler
from helpers import route

logger = logging.getLogger(__name__)

try:
    from users.handlers.login import *
    from users.handlers.update import *
    from items.handlers import *
    from tags.handler import *
    from admin.handlers.tags import *
    from admin.handlers.users import *
    from admin.handlers.login import *
except ImportError:
    logger.debug(ImportError)
__author__ = 'ne_luboff'




@route('test')
class Test(OpenApiHandler):
    allowed_methods = ('GET')

    def read(self):
        return {
            'info': "Hawkist API server",
            'server_date': datetime.datetime.now().isoformat()
        }


