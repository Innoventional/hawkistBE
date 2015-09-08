import logging
import datetime
from api.items.models import Listing
from api.items.reported_items.models import ListingReportingReasons, ReportedListings
from base import ApiHandler, die
from helpers import route
from ui_messages.errors.items_errors.items_errors import GET_LISTING_INVALID_ID
from ui_messages.errors.items_errors.reported_listings_errors import REPORT_LISTING_INVALID_REASON_ID, \
    REPORT_LISTING_TRY_REPORT_OWN_LISTING, REPORT_LISTING_ALREADY_BLOCKED_USER, REPORT_LISTING_NO_LISTING_ID, \
    REPORT_LISTING_NO_REASON_ID
from utility.user_utility import update_user_last_activity, check_user_suspension_status

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('listing/reporting')
class ReportListingsHandler(ApiHandler):
    allowed_methods = ('POST', )

    def create(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        logger.debug('REQUEST_OBJECT_REPORT_LISTING')
        logger.debug(self.request_object)

        listing_to_report_id = None
        listing_report_reason = None

        # try get id and reason to report user
        if self.request_object:
            if 'listing_id' in self.request_object:
                listing_to_report_id = self.request_object['listing_id']

            if 'reason_id' in self.request_object:
                listing_report_reason = self.request_object['reason_id']

        if not listing_to_report_id:
            return self.make_error(REPORT_LISTING_NO_LISTING_ID)

        if len(str(listing_report_reason)) == 0:
            return self.make_error(REPORT_LISTING_NO_REASON_ID)

        # check reporting reason
        if not ListingReportingReasons.tostring(listing_report_reason):
            return self.make_error(REPORT_LISTING_INVALID_REASON_ID % listing_report_reason)

        # try get listing to report by id
        listing_to_report = self.session.query(Listing).get(listing_to_report_id)

        # if where is no listing to report in our db
        if not listing_to_report:
            return self.make_error(GET_LISTING_INVALID_ID % listing_to_report_id)

        # maybe you try report your own listings
        if str(self.user.id) == str(listing_to_report.user.id):
            return self.make_error(REPORT_LISTING_TRY_REPORT_OWN_LISTING)

        # check do you block this user
        if listing_to_report.user in self.user.blocked:
            return self.make_error(REPORT_LISTING_ALREADY_BLOCKED_USER % listing_to_report.user.username.upper())

        # else add new report about this user
        report = ReportedListings()
        report.created_at = datetime.datetime.utcnow()
        report.updated_at = datetime.datetime.utcnow()
        report.user_id = self.user.id
        report.listing_id = listing_to_report.id
        report.reason = listing_report_reason

        self.session.add(report)
        self.session.commit()

        return self.success()