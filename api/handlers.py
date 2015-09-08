import logging

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)

try:
    from users.handlers.login import *
    from users.handlers.update import *
    from users.handlers.personalization import *
    from users.handlers.socials import *
    from items.handlers import *
    from items.reported_items.handlers import *
    from tags.handler import *
    from admin.handlers.users.users import *
    from admin.handlers.users.suspended_users import *
    from admin.handlers.users.blocked_users import *
    from admin.handlers.users.reported_users import *
    from admin.handlers.login import *
    from admin.handlers.metatags.metatags import *
    from admin.handlers.metatags.platforms import *
    from admin.handlers.metatags.categories import *
    from admin.handlers.metatags.subcategories import *
    from admin.handlers.metatags.colours import *
    from admin.handlers.metatags.conditions import *
    from admin.handlers.listings.listings import *
    from admin.handlers.listings.issued_listings import *
    from admin.handlers.listings.listing_by_id import *
    from admin.handlers.withdrawal import *
    from followers.handlers import *
    from comments.handlers import *
    from offers.handlers import *
    from users.blocked_users.handlers import *
    from users.reported_users.handlers import *
    from api.payments.handlers import *
    from orders.handlers import *
    from addresses.handlers import *
    from feedbacks.handlers import *
    from bank_accounts.handlers import *
    from notifications.handlers import *
except ImportError:
    logger.debug(ImportError)


@route('test')
class Test(OpenApiHandler):
    allowed_methods = ('GET', )

    def read(self):
        return {
            'info': "Hawkist API server",
            'server_date': datetime.datetime.now().isoformat()
        }