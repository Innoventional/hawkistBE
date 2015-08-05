import logging
import datetime
from api.comments.models import Comment
from api.items.models import Listing
from api.offers.models import Offer, OfferStatus
from api.users.models import SystemStatus
from base import ApiHandler, die
from environment import env
from helpers import route
from ui_messages.errors.items_errors.items_errors import GET_LISTING_INVALID_ID
from ui_messages.errors.offers_errors.offers_errors import GET_OFFERS_NO_LISTING_ID, CREATE_OFFER_NO_LISTING_ID, \
    CREATE_OFFER_EMPTY_DATA, UPDATE_OFFER_NO_NEW_STATUS, UPDATE_OFFER_INVALID_STATUS, UPDATE_OFFER_NO_OFFER_ID, \
    UPDATE_OFFER_INVALID_OFFER_ID, CREATE_OFFER_YOU_OWN_LISTING, GET_OFFERS_ANOTHER_OWNER, REACH_OFFER_LIMIT, \
    CREATE_OFFER_OFFERED_PRICE_MUST_BE_LESS_THAN_RETAIL
from ui_messages.errors.users_errors.blocked_users_error import GET_BLOCKED_USER
from ui_messages.errors.users_errors.suspended_users_errors import GET_SUSPENDED_USER
from ui_messages.messages.offers_messages import OFFER_NEW, OFFER_ACCEPTED, OFFER_DECLINED
from utility.items import calculate_discount_value
from utility.user_utility import update_user_last_activity, check_user_suspension_status

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('listings/offers/(.*)')
class ItemOffersHandler(ApiHandler):
    allowed_methods = ('POST', 'PUT')

    def create(self, listing_id):

        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        logger.debug('REQUEST_OBJECT_NEW_OFFER')
        logger.debug(self.request_object)

        # first validate listing
        if not listing_id:
            return self.make_error(CREATE_OFFER_NO_LISTING_ID)

        listing = self.session.query(Listing).get(listing_id)

        if not listing:
            return self.make_error(GET_LISTING_INVALID_ID % listing_id)

        # check listing owner
        if str(listing.user_id) == str(self.user.id):
            return self.make_error(CREATE_OFFER_YOU_OWN_LISTING)

        # check access to current profile
        if self.user in listing.user.blocked:
            return self.make_error(GET_BLOCKED_USER % listing.user.username.upper())

        # check is listing owner active
        if listing.user.system_status == SystemStatus.Suspended:
            return self.make_error(GET_SUSPENDED_USER % listing.user.username.upper())

        # check is offer available for current user today
        # get all user offers
        all_user_offers = self.session.query(Offer).filter(Offer.user_id == self.user.id)
        # get today offers
        today_user_offers = [o for o in all_user_offers
                             if o.created_at.strftime("%Y-%m-%d") == datetime.datetime.utcnow().strftime("%Y-%m-%d")]
        if len(today_user_offers) >= env['offer_limit_per_day']:
            return self.make_error(REACH_OFFER_LIMIT)

        new_price = None

        # next validate input data
        if self.request_object:
            if 'new_price' in self.request_object:
                new_price = self.request_object['new_price']

        if not new_price:
            return self.make_error(CREATE_OFFER_EMPTY_DATA)

        # check is retail price more than new price
        if float(new_price) >= float(listing.retail_price):
            return self.make_error(CREATE_OFFER_OFFERED_PRICE_MUST_BE_LESS_THAN_RETAIL
                                   % "%.02f" % float(listing.retail_price))

        # create an offer
        offer = Offer()
        offer.created_at = datetime.datetime.utcnow()
        offer.listing = listing
        offer.user = self.user
        offer.new_price = float(new_price)
        self.session.add(offer)
        self.session.commit()

        # create comment
        comment = Comment()
        comment.created_at = datetime.datetime.utcnow()
        comment.listing = listing
        comment.user = self.user
        comment.text = OFFER_NEW % "%.02f" % float(offer.new_price)
        comment.offer = offer
        # this comment can see only listing owner
        # comment.user_to_see_id = listing.user_id
        self.session.add(comment)
        self.session.commit()
        return self.success()

    def update(self, offer_id):

        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        logger.debug('REQUEST_OBJECT_CHANGE_OFFER_STATUS')
        logger.debug(self.request_object)

        # first validate offer
        if not offer_id:
            return self.make_error(UPDATE_OFFER_NO_OFFER_ID)

        offer = self.session.query(Offer).get(offer_id)
        if not offer:
            return self.make_error(UPDATE_OFFER_INVALID_OFFER_ID % offer_id)

        new_status = None

        # next validate input data
        if self.request_object:
            if 'new_status' in self.request_object:
                new_status = self.request_object['new_status']

        if not new_status:
            return self.make_error(UPDATE_OFFER_NO_NEW_STATUS)

        if str(new_status) not in ['1', '2']:
            return self.make_error(UPDATE_OFFER_INVALID_STATUS)

        if str(new_status) == '1':
            # update offer
            offer.status = OfferStatus.Accepted

            # update discount
            offer.listing.discount = calculate_discount_value(offer.listing.retail_price, offer.new_price)
            # update listing price
            offer.listing.selling_price = offer.new_price

            # create comment
            comment = Comment()
            comment.created_at = datetime.datetime.utcnow()
            comment.listing = offer.listing
            comment.user = self.user
            comment.text = OFFER_ACCEPTED % "%.02f" % float(offer.new_price)
            self.session.add(comment)
            self.session.commit()

        elif str(new_status) == '2':
            offer.status = OfferStatus.Declined

            # create comment
            comment = Comment()
            comment.created_at = datetime.datetime.utcnow()
            comment.listing = offer.listing
            comment.user = self.user
            comment.text = OFFER_DECLINED % "%.02f" % float(offer.new_price)
            self.session.add(comment)
            self.session.commit()

        return self.success()

