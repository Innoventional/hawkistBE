import logging
import datetime
from sqlalchemy import or_
from api.admin.handlers.login import AdminBaseHandler
from api.items.models import Listing, ListingStatus
from api.orders.models import UserOrders, OrderStatus, IssueStatus, IssueReason
from base import HttpRedirect
from helpers import route
from utility.notifications import notification_funds_released
from utility.send_email import listing_with_issue_investigation_opened_buyer, transaction_canceled, refunds_issues_buyer, \
    investigation_resolved

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('admin/listings/issues/(.*)')
class AdminIssuedListingsHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'PUT')

    def read(self, issue_status):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        # issue_status = self.get_arg('status')

        orders = self.session.query(UserOrders).filter(UserOrders.order_status == OrderStatus.HasAnIssue).order_by(UserOrders.issue_status)

        q = self.get_argument('q')

        if q:
            orders = orders.filter(UserOrders.listing.has(Listing.title.ilike(u'%{0}%'.format(q))))

        if issue_status == 'investigating':
            orders = orders.filter(UserOrders.issue_status == IssueStatus.Investigating).order_by(UserOrders.updated_at)
            template_name = 'admin/listings/issued/admin_investigating_issued_listings.html'
        elif issue_status == 'canceled':
            orders = orders.filter(or_(UserOrders.issue_status == IssueStatus.Cancelled,
                                       UserOrders.issue_status == IssueStatus.RefundIssued)).order_by(UserOrders.updated_at)
            template_name = 'admin/listings/issued/admin_canceled_issued_listings.html'
        elif issue_status == 'resolved':
            orders = orders.filter(UserOrders.issue_status == IssueStatus.Resolved).order_by(UserOrders.updated_at)
            template_name = 'admin/listings/issued/admin_resolved_issued_listings.html'
        else:
            orders = orders.filter(UserOrders.issue_status == IssueStatus.New).order_by(UserOrders.updated_at)
            template_name = 'admin/listings/issued/admin_new_issued_listings.html'

        return self.render_string(template_name, orders=orders,
                                  menu_tab_active='tab_listings', IssueStatus=IssueStatus, issue_type=issue_status,
                                  timedelta=datetime.timedelta, q=q, IssueReason=IssueReason)

    def update(self, issue_status):
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
            listing_with_issue_investigation_opened_buyer(order)
        elif str(action) == str(IssueStatus.Cancelled):
            order.issue_status = IssueStatus.Cancelled
            # TODO money to buyer
            order.listing.user.app_wallet_pending -= order.charge.payment_sum_without_application_fee
            order.user.app_wallet += order.charge.payment_sum
            order.listing.status = ListingStatus.Active
            # send email to seller
            transaction_canceled(order.listing.user.email, order.listing.user.username, order.listing.title)
            # send email to buyer
            transaction_canceled(order.user.email, order.user.username, order.listing.title)
            refunds_issues_buyer(order)

            #
            investigation_resolved(order.listing.user.email, order.listing.user.username, order.listing.title)
            investigation_resolved(order.user.email, order.user.username, order.listing.title)
        elif str(action) == str(IssueStatus.Resolved):
            order.issue_status = IssueStatus.Resolved
            # TODO money to seller
            order.listing.user.app_wallet_pending -= order.charge.payment_sum_without_application_fee
            order.listing.user.app_wallet += order.charge.payment_sum_without_application_fee
            order.listing.status = ListingStatus.Sold

            notification_funds_released(self.session, order.user, order.listing)

            investigation_resolved(order.listing.user.email, order.listing.user.username, order.listing.title)
            investigation_resolved(order.user.email, order.user.username, order.listing.title)
        order.updated_at = datetime.datetime.utcnow()
        self.session.commit()
        return self.success()
