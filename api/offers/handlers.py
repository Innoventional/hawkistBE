import logging
import datetime
from sqlalchemy import and_
from api.comments.models import Comment
from api.items.models import Listing
from api.offers.models import Offer, OfferStatus
from base import ApiHandler, die
from helpers import route
from ui_messages.errors.items_errors.items_errors import GET_LISTING_INVALID_ID
from ui_messages.errors.offers_errors.offers_errors import GET_OFFERS_NO_LISTING_ID, CREATE_OFFER_NO_LISTING_ID, \
    CREATE_OFFER_EMPTY_DATA, UPDATE_OFFER_NO_NEW_STATUS, UPDATE_OFFER_INVALID_STATUS, UPDATE_OFFER_NO_OFFER_ID, \
    UPDATE_OFFER_INVALID_OFFER_ID
from ui_messages.messages.offers_messages import OFFER_NEW, OFFER_ACCEPTED, OFFER_DECLINED
from utility.user_utility import update_user_last_activity, check_user_suspension_status

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)

@route('listings/offers/(.*)')
class ItemOffersHandler(ApiHandler):
    allowed_methods = ('GET', 'POST', 'PUT')

    def read(self, listing_id):

        if self.user is None:
            die(401)

        update_user_last_activity(self)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            return self.make_error(suspension_error)

        if not listing_id:
            return self.make_error(GET_OFFERS_NO_LISTING_ID)

        listing = self.session.query(Listing).get(listing_id)

        if not listing:
            return self.make_error(GET_LISTING_INVALID_ID % listing_id)

        listing_offers = self.session.query(Offer).filter(and_(Offer.listing_id == listing_id,
                                                               Offer.status == OfferStatus.Active)).order_by(Offer.created_at)
        return self.success({'offers': [o.response for o in listing_offers]})

    def create(self, listing_id):

        if self.user is None:
            die(401)

        update_user_last_activity(self)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            return self.make_error(suspension_error)

        logger.debug('REQUEST_OBJECT_NEW_OFFER')
        logger.debug(self.request_object)

        # first validate listing
        if not listing_id:
            return self.make_error(CREATE_OFFER_NO_LISTING_ID)

        listing = self.session.query(Listing).get(listing_id)

        if not listing:
            return self.make_error(GET_LISTING_INVALID_ID % listing_id)

        new_price = None

        # next validate input data
        if self.request_object:
            if 'new_price' in self.request_object:
                new_price = self.request_object['new_price']

        if not new_price:
            return self.make_error(CREATE_OFFER_EMPTY_DATA)

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
        comment.text = OFFER_NEW % (self.user.username, float(offer.new_price))
        self.session.add(comment)
        self.session.commit()
        return self.success()

    def update(self, offer_id):

        if self.user is None:
            die(401)

        update_user_last_activity(self)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            return self.make_error(suspension_error)

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

        if new_status == 1:
            # update offer
            offer.status = OfferStatus.Accepted

            # update listing price
            offer.listing.selling_price = offer.new_price

            # create comment
            comment = Comment()
            comment.created_at = datetime.datetime.utcnow()
            comment.listing = offer.listing
            comment.user = self.user
            comment.text = OFFER_ACCEPTED % (self.user.username, float(offer.new_price))
            self.session.add(comment)
            self.session.commit()

        elif new_status == 2:
            offer.status = OfferStatus.Declined

            # create comment
            comment = Comment()
            comment.created_at = datetime.datetime.utcnow()
            comment.listing = offer.listing
            comment.user = self.user
            comment.text = OFFER_DECLINED % (self.user.username, float(offer.new_price))
            self.session.add(comment)
            self.session.commit()

        return self.success()
