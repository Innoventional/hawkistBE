import logging
from api.admin.handlers.tags import AdminBaseHandler
from api.items.models import Listing
from base import HttpRedirect, paginate
from helpers import route
from ui_messages.errors.admin_errors.admin_listings_errors import ADMIN_TRY_DELETE_LISTING_WHICH_DOES_NOT_EXISTS

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('admin/listings')
class AdminListingsHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'DELETE')

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        listings = self.session.query(Listing).order_by(Listing.id)

        page = self.get_arg('p', int, 1)
        page_size = self.get_arg('page_size', int, 100)
        paginator, listings = paginate(listings, page, page_size)

        return self.render_string('admin/admin_listings.html', listings=listings, paginator=paginator,
                                  menu_tab_active='tab_listings')

    def remove(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        listing_id = self.get_arg('listing_id')
        listing = self.session.query(Listing).filter(Listing.id == listing_id).first()

        if not listing:
            return self.make_error(ADMIN_TRY_DELETE_LISTING_WHICH_DOES_NOT_EXISTS % listing_id)

        self.session.delete(listing)
        self.session.commit()
        return self.success()
