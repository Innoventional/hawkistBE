import logging
import datetime
from sqlalchemy import or_
from api.admin.handlers.login import AdminBaseHandler
from api.items.models import Listing, ListingStatus
from api.orders.models import UserOrders, OrderStatus, IssueStatus
from base import HttpRedirect, paginate
from helpers import route
from ui_messages.errors.admin_errors.admin_listings_errors import ADMIN_TRY_DELETE_LISTING_WHICH_DOES_NOT_EXISTS

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('admin/listings/issues')
class AdminIssuedListingsHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'PUT')

    def read(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        issue_status = self.get_arg('status')

        orders = self.session.query(UserOrders).filter(UserOrders.order_status == OrderStatus.HasAnIssue).order_by(UserOrders.issue_status)

        if issue_status == 'investigating':
            orders = orders.filter(UserOrders.issue_status == IssueStatus.Investigating).order_by(UserOrders.updated_at)
            return self.render_string('admin/listings/issued/admin_investigating_issued_listings.html', orders=orders,
                                      menu_tab_active='tab_listings', IssueStatus=IssueStatus, issue_type=issue_status,
                                      timedelta=datetime.timedelta)
        elif issue_status == 'canceled':
            orders = orders.filter(or_(UserOrders.issue_status == IssueStatus.Cancelled,
                                       UserOrders.issue_status == IssueStatus.RefundIssued)).order_by(UserOrders.updated_at)
            return self.render_string('admin/listings/issued/admin_canceled_issued_listings.html', orders=orders,
                                      menu_tab_active='tab_listings', IssueStatus=IssueStatus, issue_type=issue_status,
                                      timedelta=datetime.timedelta)
        elif issue_status == 'resolved':
            orders = orders.filter(UserOrders.issue_status == IssueStatus.Resolved).order_by(UserOrders.updated_at)
            return self.render_string('admin/listings/issued/admin_resolved_issued_listings.html', orders=orders,
                                      menu_tab_active='tab_listings', IssueStatus=IssueStatus, issue_type=issue_status,
                                      timedelta=datetime.timedelta)
        else:
            orders = orders.filter(UserOrders.issue_status == IssueStatus.New).order_by(UserOrders.updated_at)
            return self.render_string('admin/listings/issued/admin_new_issued_listings.html', orders=orders,
                                      menu_tab_active='tab_listings', IssueStatus=IssueStatus, issue_type=issue_status,
                                      timedelta=datetime.timedelta)

    def update(self):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        order_id = self.get_arg('id')
        action = self.get_arg('action')
        order = self.session.query(UserOrders).filter(UserOrders.id == order_id).first()

        if not order:
            logger.debug('UPDATE ORDER')
            logger.debug(order_id)
            return self.make_error('Something wrong')

        if str(action) == str(IssueStatus.Investigating):
            order.issue_status = IssueStatus.Investigating
        elif str(action) == str(IssueStatus.Cancelled):
            order.issue_status = IssueStatus.Cancelled
            # TODO money to buyer
            order.listing.user.app_wallet_pending -= order.charge.payment_sum_without_application_fee
            order.user.app_wallet += order.charge.payment_sum_without_application_fee
            order.listing.status = ListingStatus.Active
        elif str(action) == str(IssueStatus.Resolved):
            order.issue_status = IssueStatus.Resolved
            # TODO money to seller
            order.listing.user.app_wallet_pending -= order.charge.payment_sum_without_application_fee
            order.listing.user.app_wallet += order.charge.payment_sum_without_application_fee
            order.listing.status = ListingStatus.Sold
        order.updated_at = datetime.datetime.utcnow()
        self.session.commit()
        return self.success()
