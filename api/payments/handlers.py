import logging
import datetime
from api.items.models import Listing, ListingStatus
from api.payments.models import StripeCustomer, StripeCharges, ChargesStatus
from base import ApiHandler, die
from environment import env
from helpers import route
from ui_messages.errors.items_errors.items_errors import GET_LISTING_INVALID_ID
from ui_messages.errors.payment_errors import ADD_CARD_EMPTY_FIELDS, ADD_CARD_NO_STRIPE_TOKEN, UPDATE_CARD_EMPTY_FIELDS, \
    BANK_CARD_ALREADY_USED, UPDATE_CARD_NO_ID, UPDATE_CARD_INVALID_ID, DELETE_CARD_NO_CARD_ID, CREATE_CHARGE_NO_CARD_ID, \
    CREATE_CHARGE_NO_STRIPE_ACCOUNT, CREATE_CHARGE_NO_LISTING_ID, CREATE_CHARGE_BUY_YOUR_OWN_LISTING, \
    CREATE_CHARGE_BUY_RESERVED_LISTING, CREATE_CHARGE_BUY_SOLD_LISTING
from ui_messages.messages.custom_error_titles import CREATE_LISTING_EMPTY_FIELDS_TITLE
from utility.stripe_api import stripe_create_customer, stripe_retrieve_customer, stripe_retrieve_card_info, \
    stripe_retrieve_card, stripe_update_card_info, stripe_add_new_card, stripe_delete_card, stripe_create_charges
from utility.user_utility import update_user_last_activity, check_user_suspension_status

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


# add new card and create stripe card/customer
@route('user/cards')
class CardHandler(ApiHandler):
    allowed_methods = ('POST', 'GET', 'PUT', 'DELETE')

    def read(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        card_response = []
        # select all users cards
        cards = self.user.stripe_customer
        # retrieve stripe acc
        customer_response = stripe_retrieve_customer(cards.stripe_customer_id)
        # get info for every card
        customer_cards = customer_response['sources']['data']
        if customer_cards:
            for customer_card in customer_cards:
                card_response.append(stripe_retrieve_card_info(customer_card))
        return self.success({
            'cards': card_response
        })

    def create(self):

        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        logger.debug('REQUEST_OBJECT_ADD_NEW_CARD')
        logger.debug(self.request_object)

        stripe_token = ''

        if self.request_object:
            if 'stripe_token' in self.request_object:
                stripe_token = self.request_object['stripe_token']

        if not stripe_token:
            return self.make_error(ADD_CARD_NO_STRIPE_TOKEN)

        # first check have this user stripe customer
        if self.user.stripe_customer:
            logger.debug('Add new card to existing stripe account')
            # get customer object
            stripe_customer = stripe_retrieve_customer(self.user.stripe_customer.stripe_customer_id)
            # add new stripe card to existing customer
            error = stripe_add_new_card(stripe_customer, stripe_token)
            if error:
                return self.make_error(error)
            self.user.stripe_customer.updated_at = datetime.datetime.utcnow()
        else:
            logger.debug('Create new stripe account')
            # create new customer
            # first try create stripe customer object
            stripe_response = stripe_create_customer(stripe_token, self.user.id)
            logger.debug('CREATE_CUSTOMER_STRIPE_RESPONSE')
            logger.debug(stripe_response)
            stripe_error, stripe_data = stripe_response['error'], stripe_response['data']
            if stripe_error:
                return self.make_error(stripe_error)

            # get customer id and card id from stripe response
            customer_id = stripe_data['id']
            stripe_card_id = stripe_data['sources']['data'][0]['id']

            stripe_customer = StripeCustomer()
            stripe_customer.created_at = datetime.datetime.utcnow()
            stripe_customer.updated_at = datetime.datetime.utcnow()
            stripe_customer.stripe_customer_id = customer_id
            stripe_customer.stripe_card_id = stripe_card_id
            self.session.add(stripe_customer)

            # set relationship to stripe account
            self.user.stripe_customer = stripe_customer
        self.session.commit()
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

        logger.debug('REQUEST_OBJECT_UPDATE_CARD')
        logger.debug(self.request_object)

        stripe_card_id = ''
        name = ''
        exp_month = ''
        exp_year = ''
        address_line1 = ''
        address_line2 = ''
        city = ''
        postcode = ''

        if self.request_object:
            if 'id' in self.request_object:
                stripe_card_id = self.request_object['id']

            if 'name' in self.request_object:
                name = self.request_object['name']

            if 'exp_month' in self.request_object:
                exp_month = self.request_object['exp_month']

            if 'exp_year' in self.request_object:
                exp_year = self.request_object['exp_year']

            if 'address_line1' in self.request_object:
                address_line1 = self.request_object['address_line1']

            if 'address_line2' in self.request_object:
                address_line2 = self.request_object['address_line2']

            if 'city' in self.request_object:
                city = self.request_object['city']

            if 'postcode' in self.request_object:
                postcode = self.request_object['postcode']

        empty_field_error = []

        if not name:
            empty_field_error.append('cardholder name')

        if not exp_month:
            empty_field_error.append('expiration month')

        if not exp_year:
            empty_field_error.append('expiration year')

        if not address_line1:
            empty_field_error.append('address line 1')

        if not address_line2:
            empty_field_error.append('address line 2')

        if not city:
            empty_field_error.append('city')

        if not postcode:
            empty_field_error.append('postcode')

        if not stripe_card_id:
            return self.make_error(UPDATE_CARD_NO_ID)

        if empty_field_error:
            empty_fields = ', '.join(empty_field_error)
            return self.make_error(message=UPDATE_CARD_EMPTY_FIELDS % empty_fields,
                                   title=CREATE_LISTING_EMPTY_FIELDS_TITLE % empty_fields.capitalize())

        # first get customer
        if not self.user.stripe_customer:
            return self.make_error(CREATE_CHARGE_NO_STRIPE_ACCOUNT)

        stripe_customer = stripe_retrieve_customer(self.user.stripe_customer.stripe_customer_id)

        # check is any card in this stripe account
        stripe_customer_cards = stripe_customer['sources']['data']
        if stripe_card_id not in str(stripe_customer_cards):
            return self.make_error(UPDATE_CARD_INVALID_ID % stripe_card_id)

        stripe_card = stripe_retrieve_card(stripe_customer, stripe_card_id)

        # update card
        stripe_update_card_info(stripe_card, name=name, exp_month=exp_month, exp_year=exp_year,
                                address_line1=address_line1, address_line2=address_line2, city=city, postcode=postcode)
        self.user.stripe_customer.updated_at = datetime.datetime.utcnow()
        self.session.commit()
        return self.success()

    def remove(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        card_to_delete_id = self.get_arg('card_id', None)

        if not card_to_delete_id:
            return self.make_error(DELETE_CARD_NO_CARD_ID)

        # first get customer
        if not self.user.stripe_customer:
            return self.make_error('NO STRIPE CUSTOMER')

        stripe_customer = stripe_retrieve_customer(self.user.stripe_customer.stripe_customer_id)

        # check is any card in this stripe account
        stripe_customer_cards = stripe_customer['sources']['data']
        if card_to_delete_id not in str(stripe_customer_cards):
            return self.make_error(UPDATE_CARD_INVALID_ID % card_to_delete_id)

        stripe_card = stripe_retrieve_card(stripe_customer, card_to_delete_id)
        stripe_delete_error = stripe_delete_card(stripe_card)
        if stripe_delete_error:
            return self.make_error(stripe_delete_error)
        self.user.stripe_customer.updated_at = datetime.datetime.utcnow()
        self.session.commit()
        return self.success()

    # TODO first edition. With all card info
    # def create(self):
    #
    #     if self.user is None:
    #         die(401)
    #
    #     logger.debug(self.user)
    #     update_user_last_activity(self)
    #
    #     suspension_error = check_user_suspension_status(self.user)
    #     if suspension_error:
    #         logger.debug(suspension_error)
    #         return suspension_error
    #
    #     # id field to know is it request to create or update card
    #     card_id = ''
    #     # first get all required data to create card
    #     name = ''
    #     card_number = ''
    #     cvv = ''
    #     exp_month = ''
    #     exp_year = ''
    #     address_line1 = ''
    #     address_line2 = ''
    #     city = ''
    #     postcode = ''
    #     stripe_token = ''
    #
    #     if self.request_object:
    #         if 'id' in self.request_object:
    #             card_id = self.request_object['id']
    #
    #         if 'name' in self.request_object:
    #             name = self.request_object['name']
    #
    #         if 'card_number' in self.request_object:
    #             card_number = self.request_object['card_number']
    #
    #         if 'cvv' in self.request_object:
    #             cvv = self.request_object['cvv']
    #
    #         if 'exp_month' in self.request_object:
    #             exp_month = self.request_object['exp_month']
    #
    #         if 'exp_year' in self.request_object:
    #             exp_year = self.request_object['exp_year']
    #
    #         if 'address_line1' in self.request_object:
    #             address_line1 = self.request_object['address_line1']
    #
    #         if 'address_line2' in self.request_object:
    #             address_line2 = self.request_object['address_line2']
    #
    #         if 'city' in self.request_object:
    #             city = self.request_object['city']
    #
    #         if 'postcode' in self.request_object:
    #             postcode = self.request_object['postcode']
    #
    #         if 'stripe_token' in self.request_object:
    #             stripe_token = self.request_object['stripe_token']
    #
    #     empty_field_error = []
    #
    #     if not name:
    #         empty_field_error.append('cardholder name')
    #
    #     if not card_number:
    #         empty_field_error.append('card number')
    #
    #     if not cvv:
    #         empty_field_error.append('cvv number')
    #
    #     if not exp_month:
    #         empty_field_error.append('expiration month')
    #
    #     if not exp_year:
    #         empty_field_error.append('expiration year')
    #
    #     if not address_line1:
    #         empty_field_error.append('address line 1')
    #
    #     if not address_line2:
    #         empty_field_error.append('address line 2')
    #
    #     if not city:
    #         empty_field_error.append('city')
    #
    #     if not postcode:
    #         empty_field_error.append('postcode')
    #
    #     if not stripe_token:
    #         return self.make_error(ADD_CARD_NO_STRIPE_TOKEN)
    #
    #     if card_id:
    #         # this is update card request
    #         print 'in update'
    #         logger.debug('REQUEST_OBJECT_UPDATE_CARD')
    #         logger.debug(self.request_object)
    #
    #         if empty_field_error:
    #             empty_fields = ', '.join(empty_field_error)
    #             return self.make_error(message=UPDATE_CARD_EMPTY_FIELDS % empty_fields,
    #                                    title=CREATE_LISTING_EMPTY_FIELDS_TITLE % empty_fields.capitalize())
    #
    #     else:
    #         logger.debug('REQUEST_OBJECT_ADD_NEW_CARD')
    #         logger.debug(self.request_object)
    #
    #         if empty_field_error:
    #             empty_fields = ', '.join(empty_field_error)
    #             return self.make_error(message=ADD_CARD_EMPTY_FIELDS % empty_fields,
    #                                    title=CREATE_LISTING_EMPTY_FIELDS_TITLE % empty_fields.capitalize())
    #
    #         # format bank card number
    #         card_number = card_number.replace(' ', '')
    #         # check is this card already in use
    #         already_used = self.session.query(Card).filter(Card.number == card_number).first()
    #         if already_used:
    #             return self.make_error(BANK_CARD_ALREADY_USED)
    #
    #         # first try create stripe customer object
    #         stripe_response = stripe_create_customer(stripe_token, name)
    #         logger.debug('CREATE_CUSTOMER_STRIPE_RESPONSE')
    #         logger.debug(stripe_response)
    #         stripe_error, stripe_data = stripe_response['error'], stripe_response['data']
    #         if stripe_error:
    #             return self.make_error(stripe_error)
    #         # get customer id and card id from stripe response
    #         customer_id = stripe_response['id']
    #         stripe_card_id = stripe_response['sources']['data'][0]['id']
    #
    #         stripe_customer = StripeCustomer()
    #         stripe_customer.created_at = datetime.datetime.utcnow()
    #         stripe_customer.updated_at = datetime.datetime.utcnow()
    #         stripe_customer.stripe_customer_id = customer_id
    #         stripe_customer.stripe_card_id = stripe_card_id
    #         self.session.add(stripe_customer)
    #
    #         # after it create new card object
    #         card = Card()
    #         card.created_at = datetime.datetime.utcnow()
    #         card.updated_at = datetime.datetime.utcnow()
    #         card.user = self.user
    #         card.name = name
    #         card.number = card_number
    #         card.cvv = cvv
    #         card.exp_month = exp_month
    #         card.exp_year = exp_year
    #         card.address_line1 = address_line1
    #         card.address_line2 = address_line2
    #         card.address_city = city
    #         card.address_postcode = postcode
    #
    #         # set relationship to stripe account
    #         card.stripe_customer = stripe_customer
    #         self.session.add(card)
    #
    #         # finally make this card current user card
    #         self.user.stripe_customer = stripe_customer
    #         self.session.commit()
    #     return self.success()


@route('listings/buy')
class BuyListingHandler(ApiHandler):
    allowed_methods = ('POST', 'PUT')

    def create(self):

        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        logger.debug('REQUEST_OBJECT_ADD_NEW_CHARGE')
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

        # stripe_card = stripe_retrieve_card(stripe_customer, stripe_card_id)

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
        new_charge.application_fee_sum = float(listing.selling_price) * env['stripe_hawkist_fee_persentage']
        new_charge.transaction_status = stripe_charge['status']

        new_charge.buyer_id = self.user.id
        new_charge.listing_id = listing.id
        self.session.add(new_charge)
        self.session.commit()
        return self.success()