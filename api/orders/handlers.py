import datetime
import tornado
from api.items.models import Listing, ListingStatus
from api.orders.models import UserOrders, OrderStatus, IssueStatus
from api.payments.models import StripeCharges, ChargesStatus
from base import ApiHandler, die, logger
from environment import env
from helpers import route
from ui_messages.errors.items_errors.items_errors import GET_LISTING_INVALID_ID
from ui_messages.errors.orders_errors import UPDATE_ORDER_NO_ID, UPDATE_ORDER_NO_STATUS, UPDATE_ORDER_NO_REASON, \
    UPDATE_ORDER_NO_ORDER, UPDATE_ORDER_ORDER_NOT_ACTIVE, UPDATE_ORDER_INVALID_STATUS, UPDATE_ODER_INVALID_ISSUE_REASON
from ui_messages.errors.payment_errors import CREATE_CHARGE_NO_CARD_ID, CREATE_CHARGE_NO_LISTING_ID, \
    CREATE_CHARGE_BUY_YOUR_OWN_LISTING, CREATE_CHARGE_BUY_RESERVED_LISTING, CREATE_CHARGE_BUY_SOLD_LISTING, \
    CREATE_CHARGE_NO_STRIPE_ACCOUNT, UPDATE_CARD_INVALID_ID
from utility.payment import check_pending_payments
from utility.send_email import purchase_confirmation_sending_buyer, purchase_confirmation_sending_seller, \
    listing_with_issue_seller, listing_received_seller
from utility.stripe_api import stripe_retrieve_customer, stripe_create_charges
from utility.user_utility import update_user_last_activity, check_user_suspension_status
from tornado import ioloop

__author__ = 'ne_luboff'


@route('user/orders')
class OrdersHandler(ApiHandler):
    allowed_methods = ('POST', 'PUT', 'GET')

    def read(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        orders = self.user.user_orders

        # search in orders. search by title and platform name. search for every word in searching query
        searching_query = self.get_arg("q")
        if searching_query:
            searching_query_dict = searching_query.lower().split(' ')
            suitable_orders = set()
            for o in orders:
                for q in searching_query_dict:
                    if q in o.listing.title.lower() or q in o.listing.platform.title.lower():
                        suitable_orders.add(o.id)
            orders = orders.filter(UserOrders.id.in_(list(suitable_orders)))
        return self.success(
            {'orders': [o.response for o in orders]}
        )

    def create(self):

        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        logger.debug('REQUEST_OBJECT_CREATE_ORDER_(BUY_ITEM)')
        logger.debug(self.request_object)

        stripe_card_id = ''
        listing_id = ''

        if self.request_object:
            if 'stripe_card_id' in self.request_object:
                stripe_card_id = self.request_object['stripe_card_id']

            if 'listing_id' in self.request_object:
                listing_id = self.request_object['listing_id']

        if not stripe_card_id:
            return self.make_error(CREATE_CHARGE_NO_CARD_ID)

        if not listing_id:
            return self.make_error(CREATE_CHARGE_NO_LISTING_ID)

        # validate listing
        # try get listing object
        listing = self.session.query(Listing).filter(Listing.id == listing_id).first()
        if not listing:
            return self.make_error(GET_LISTING_INVALID_ID % listing_id)

        # check listing owner
        if str(self.user.id) == str(listing.user.id):
            return self.make_error(CREATE_CHARGE_BUY_YOUR_OWN_LISTING)

        # check listing status
        if listing.status == ListingStatus.Reserved:
            return self.make_error(CREATE_CHARGE_BUY_RESERVED_LISTING)
        elif listing.status == ListingStatus.Sold:
            return self.make_error(CREATE_CHARGE_BUY_SOLD_LISTING)

        # validate card
        # check does this user has stripe customer
        if not self.user.stripe_customer:
            return self.make_error(CREATE_CHARGE_NO_STRIPE_ACCOUNT)

        stripe_customer = stripe_retrieve_customer(self.user.stripe_customer.stripe_customer_id)

        # check is any card in this stripe account
        stripe_customer_cards = stripe_customer['sources']['data']
        if stripe_card_id not in str(stripe_customer_cards):
            return self.make_error(UPDATE_CARD_INVALID_ID % stripe_card_id)

        # calculate charge amount
        amount = listing.selling_price
        if listing.shipping_price:
            amount += listing.shipping_price

        # so try create stripe charge
        stripe_response = stripe_create_charges(customer_id=self.user.stripe_customer.stripe_customer_id,
                                                card_id=stripe_card_id, amount=int(amount*100), description=listing.id)
        logger.debug('STRIPE_RESPONSE')
        logger.debug(stripe_response)

        stripe_error, stripe_charge = stripe_response['error'], stripe_response['data']
        if stripe_error:
            return self.make_error(stripe_error)

        # if this is success payment create new row in payments table
        new_charge = StripeCharges()
        new_charge.created_at = datetime.datetime.utcnow()
        new_charge.updated_at = datetime.datetime.utcnow()
        new_charge.date_finish = new_charge.created_at + datetime.timedelta(days=7)
        new_charge.system_status = ChargesStatus.Active

        new_charge.charge_id = stripe_charge['id']
        new_charge.transaction_id = stripe_charge['balance_transaction']
        new_charge.paid = stripe_charge['paid']
        new_charge.refunded = stripe_charge['refunded']
        new_charge.payment_sum = amount
        new_charge.payment_sum_without_application_fee = float(amount) - (float(listing.selling_price) * env['stripe_hawkist_fee_persentage'])
        new_charge.transaction_status = stripe_charge['status']

        new_charge.buyer_id = self.user.id
        new_charge.listing_id = listing.id
        self.session.add(new_charge)
        self.session.commit()

        # after it create new order
        new_order = UserOrders()
        new_order.created_at = datetime.datetime.utcnow()
        new_order.updated_at = datetime.datetime.utcnow()
        new_order.user_id = self.user.id
        new_order.listing_id = listing.id
        new_order.charge_id = new_charge.id
        new_order.order_status = OrderStatus.Active
        self.session.add(new_order)

        # send money to pending wallet balance
        if listing.user.app_wallet_pending:
            listing.user.app_wallet_pending += new_charge.payment_sum_without_application_fee
        else:
            listing.user.app_wallet_pending = 0
            listing.user.app_wallet_pending += new_charge.payment_sum_without_application_fee
        if not listing.user.app_wallet:
            listing.user.app_wallet = 0

        # also validate buyer wallet
        if not self.user.app_wallet:
            self.user.app_wallet = 0
        if not self.user.app_wallet_pending:
            self.user.app_wallet = 0

        listing.status = ListingStatus.Reserved

        self.session.commit()

        # send email to buyer
        purchase_confirmation_sending_buyer(self, listing)

        # send email to seller
        purchase_confirmation_sending_seller(self, listing)

        # start 3-days warning timer
        new_order.email_user_email = new_order.user.email
        new_order.email_user_username = new_order.user.username
        new_order.email_listing_title = new_order.listing.title

        new_order.warning_3_days_timer = ioloop.IOLoop.current().add_timeout(datetime.timedelta(seconds=30),
                                                                             new_order.warning_3_5_days)

        # start 5-days warning timer
        new_order.warning_5_days_timer = ioloop.IOLoop.current().add_timeout(datetime.timedelta(seconds=60),
                                                                             new_order.warning_3_5_days)

        # start timer money release
        new_order.listing_user_username = new_order.listing.user.username
        new_order.listing_title = new_order.listing.title
        new_order.order_payment_sum_without_application_fee = new_order.charge.payment_sum_without_application_fee
        new_order.listing_user_email = new_order.listing.user.email
        new_order.automatic_money_release_timer = ioloop.IOLoop.current().add_timeout(datetime.timedelta(seconds=90),
                                                                                      new_order.automatic_money_release)

        return self.success()

    def update(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        logger.debug('REQUEST_OBJECT_UPDATE_ORDER')
        logger.debug(self.request_object)

        order_id = ''
        new_status = ''
        issue_reason = ''

        if self.request_object:
            if 'order_id' in self.request_object:
                order_id = self.request_object['order_id']

            if 'new_status' in self.request_object:
                new_status = self.request_object['new_status']

            if 'issue_reason' in self.request_object:
                issue_reason = self.request_object['issue_reason']

        if not order_id:
            return self.make_error(UPDATE_ORDER_NO_ID)

        if not new_status:
            return self.make_error(UPDATE_ORDER_NO_STATUS)

        # check does user select decline order reason
        if str(new_status) == str(OrderStatus.HasAnIssue):
            if len(str(issue_reason)) == 0:
                return self.make_error(UPDATE_ORDER_NO_REASON)

        # check does this order exists
        order = self.session.query(UserOrders).get(order_id)
        if not order:
            return self.make_error(UPDATE_ORDER_NO_ORDER % order_id)

        # check is user available to change this order status
        if str(order.order_status) != str(OrderStatus.Active):
            return self.make_error(UPDATE_ORDER_ORDER_NOT_ACTIVE)

        # if new status is received we must send this money to seller
        if str(new_status) == str(OrderStatus.Received):
            order.order_status = OrderStatus.Received
            order.listing.status = ListingStatus.Sold
            order.charge.system_status = ChargesStatus.Finished

            # get money from pending balance to available
            order.listing.user.app_wallet_pending -= order.charge.payment_sum_without_application_fee
            order.listing.user.app_wallet += order.charge.payment_sum_without_application_fee
            self.session.commit()
            # send notification to seller
            listing_received_seller(self, order)

        elif str(new_status) == str(OrderStatus.HasAnIssue):
            # validate issue reason
            if str(issue_reason) not in ['0', '1', '2']:
                return self.make_error(UPDATE_ODER_INVALID_ISSUE_REASON)
            # mark this order with has issue flag
            order.order_status = OrderStatus.HasAnIssue
            order.charge.system_status = ChargesStatus.Frozen
            order.issue_reason = issue_reason
            order.issue_status = IssueStatus.New
            self.session.commit()
            # send notification to listing owner
            listing_with_issue_seller(self, order.listing)
        else:
            return self.make_error(UPDATE_ORDER_INVALID_STATUS)

        # remove timer 3 days warning
        if order.charge.warning_3_days_timer:
            tornado.ioloop.IOLoop.current().remove_timeout(order.warning_3_days_timer)
            order.warning_3_days_timer = None

        # remove timer 5 days warning
        if order.charge.warning_5_days_timer:
            tornado.ioloop.IOLoop.current().remove_timeout(order.warning_5_days_timer)
            order.warning_5_days_timer = None

        # remove timer money release
        if order.charge.automatic_money_release_timer:
            tornado.ioloop.IOLoop.current().remove_timeout(order.automatic_money_release_timer)
            order.automatic_money_release_timer = None

        return self.success()


@route('test_timer')
class TEstTimerHandler(ApiHandler):
    allowed_methods = ('GET', )

    def read(self):
        if self.user is None:
            die(401)

        # get charge
        charge = self.session.query(UserOrders).get(8)
        charge.email_user_email = charge.user.email
        charge.email_user_username = charge.user.username
        charge.email_listing_title = charge.listing.title
        charge.sellerTimeout = ioloop.IOLoop.current().add_timeout(datetime.timedelta(seconds=10),
                                                                   charge.warning_3_5_days)
        return self.success()