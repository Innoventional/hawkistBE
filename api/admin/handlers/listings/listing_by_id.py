import logging
import datetime
from api.admin.handlers.login import AdminBaseHandler
from api.items.models import Listing
from base import HttpRedirect
from helpers import route
from ui_messages.errors.admin_errors.admin_listings_errors import ADMIN_TRY_DELETE_LISTING_WHICH_DOES_NOT_EXISTS

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('admin/listings/(.*)')
class AdminListingByIdHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'DELETE')

    def read(self, listing_id):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)
        listing = ''

        try:
            listing = self.session.query(Listing).get(listing_id)
        except:
            pass

        return self.render_string('admin/listings/admin_listing_by_id.html', listing=listing,
                                  menu_tab_active='tab_listings', timedelta=datetime.timedelta)

    def remove(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        listing_id = self.get_arg('listing_id')
        listing = self.session.query(Listing).filter(Listing.id == listing_id).first()

        if not listing:
            return self.make_error(ADMIN_TRY_DELETE_LISTING_WHICH_DOES_NOT_EXISTS % listing_id)

        self.session.delete(listing)
        self.session.commit()
        return self.success()
