import logging
import datetime
from sqlalchemy import and_
from api.admin.handlers.login import AdminBaseHandler
from api.items.reported_items.models import ReportedListings, ListingReportingReasons
from api.orders.models import UserOrders, OrderStatus, IssueStatus
from base import HttpRedirect
from helpers import route

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('admin/reported_listings')
class AdminReportedListingsHandler(AdminBaseHandler):
    allowed_methods = ('GET', )

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)
        # first get all info from blocked user table

        reported_listings = self.session.query(ReportedListings).order_by(ReportedListings.id)

        new_issues = True if self.session.query(UserOrders).filter(and_(UserOrders.order_status == OrderStatus.HasAnIssue,
                                                                        UserOrders.issue_status == IssueStatus.New)).count() != 0 else False

        return self.render_string('admin/listings/admin_reported_listings.html', reported_listings=reported_listings,
                                  menu_tab_active='tab_listings', ListingReportingReasons=ListingReportingReasons,
                                  timedelta=datetime.timedelta, new_issues=new_issues)