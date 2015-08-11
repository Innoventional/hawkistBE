import logging
from sqlalchemy import and_
from api.admin.handlers.login import AdminBaseHandler
from api.items.models import Listing, ListingStatus
from api.orders.models import UserOrders, OrderStatus, IssueStatus
from base import HttpRedirect, paginate
from helpers import route
from ui_messages.errors.admin_errors.admin_listings_errors import ADMIN_TRY_DELETE_LISTING_WHICH_DOES_NOT_EXISTS
from ui_messages.errors.items_errors.items_errors import DELETE_SOLD_LISTING, DELETE_RESERVED_LISTING

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('admin/listings')
class AdminListingsHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'DELETE')

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        listings = self.session.query(Listing).order_by(Listing.id)

        page = self.get_arg('p', int, 1)
        page_size = self.get_arg('page_size', int, 100)
        paginator, listings = paginate(listings, page, page_size)

        # is any new issues
        new_issues = True if self.session.query(UserOrders).filter(and_(UserOrders.order_status == OrderStatus.HasAnIssue,
                                                                        UserOrders.issue_status == IssueStatus.New)).count() != 0 else False

        return self.render_string('admin/listings/admin_listings.html', listings=listings, paginator=paginator,
                                  menu_tab_active='tab_listings', new_issues=new_issues)

    def remove(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        listing_id = self.get_arg('listing_id')
        listing = self.session.query(Listing).filter(Listing.id == listing_id).first()

        if not listing:
            return self.make_error(ADMIN_TRY_DELETE_LISTING_WHICH_DOES_NOT_EXISTS % listing_id)

        if listing.status == ListingStatus.Reserved:
            return self.make_error(DELETE_RESERVED_LISTING)

        if listing.status == ListingStatus.Sold:
            return self.make_error(DELETE_SOLD_LISTING)

        # must delete all mentions
        # select all comments with this listing
        comments = listing.listing_comments
        for c in comments:
            # select all mentions
            comment_mentions = c.user_mentions
            for m in comment_mentions:
                comment_mentions.remove(m)
                self.session.commit()
            self.session.delete(c)
            self.session.commit()

        comments = listing.listing_comments
        for c in comments:
            # select all mentions
            comment_mentions = c.user_mentions
            for m in comment_mentions:
                comment_mentions.remove(m)
                self.session.commit()
            self.session.delete(c)
            self.session.commit()

        self.session.delete(listing)
        self.session.commit()
        return self.success()
