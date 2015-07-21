import logging

logger = logging.getLogger(__name__)

try:
    from users.handlers.login import *
    from users.handlers.update import *
    from items.handlers import *
    from tags.handler import *
    from admin.handlers.tags import *
    from admin.handlers.users import *
    from admin.handlers.login import *
    from admin.handlers.metatags.metatags import *
    from admin.handlers.metatags.platforms import *
    from admin.handlers.metatags.categories import *
    from admin.handlers.metatags.subcategories import *
    from admin.handlers.metatags.colours import *
    from admin.handlers.metatags.conditions import *
    from admin.handlers.listings import *
    from followers.handlers import *
    from comments.handlers import *
    from offers.handlers import *
    from users.blocked_users.handlers import *
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


