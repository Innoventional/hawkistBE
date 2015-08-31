import datetime
import logging
from api.items.models import Listing, ListingStatus
from api.offers.models import OfferStatus
from api.orders.models import UserOrders, OrderStatus
from api.users.models import User, SystemStatus
from orm import new_session
from utility.average_response_time import calculate_average_response_time
from utility.notifications import notification_item_received, notification_funds_released
from utility.send_email import send_warning_4_6_days_email, funds_received_seller

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


def daily_events():
    """
    Daily events are:
        - send warnings and notifications on 4th and 6th days to buyer "Is item received?"
        - automatic money release on 7th day to seller.
    """
    with new_session() as session:
        """
        Send all messages.
        Function for sending 4/6 days notification to email and user notification screen if order is active
        """
        logger.debug('Cron script started: %s' % datetime.datetime.utcnow())
        orders = session.query(UserOrders).filter(UserOrders.order_status == OrderStatus.Active)
        for order in orders:
            # check time difference
            time_delta = datetime.datetime.utcnow() - order.created_at
            if time_delta.days == 4 or time_delta.days == 6:
                # send 4/6 days warning letter
                send_warning_4_6_days_email(order.user.email, order.user.username, order.listing.title)
                # add notifications
                notification_item_received(session, order)
            elif time_delta.days == 7:
                # first we must transfer money from pending balance to available
                order.listing.user.app_wallet_pending -= order.payment_sum_without_application_fee
                order.listing.user.app_wallet += order.payment_sum_without_application_fee
                order.order_status = OrderStatus.FundsReleasedByTimer
                # send email notification to seller
                funds_received_seller(order)
                # add notification
                notification_funds_released(session, order.user, order.listing)
        session.commit()


def hourly_events():
    with new_session() as session:
        """
        Check all reserved listings
        """
        listings = session.query(Listing).filter(Listing.reserved_by_user == True)
        for listing in listings:
            time_delta = datetime.datetime.utcnow() - listing.reserve_time
            if time_delta.days >= 1:
                # make this listing available
                listing.selling_price = listing.previous_price
                listing.reserved_by_user = False
                listing.status = ListingStatus.Active
                listing.user_who_reserve_id = None
                listing.user_who_reserve = None
                listing.reserve_time = None

            # make hidden offers visible
            for offer in listing.listing_offers:
                if offer.status == OfferStatus.Active and not offer.visibility:
                    offer.visibility = True
        """
        Recalculate response time for every user
        """
        users = session.query(User).filter(User.system_status == SystemStatus.Active)
        for user in users:
            user.average_response_time = calculate_average_response_time(user)
        session.commit()
        logger.debug('Cron script finished: %s' % datetime.datetime.utcnow())