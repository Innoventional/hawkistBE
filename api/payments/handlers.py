import json
import logging
import datetime
from api.payments.models import StripeCustomer
from base import ApiHandler, die
from helpers import route
from ui_messages.errors.payment_errors import ADD_CARD_EMPTY_FIELDS, ADD_CARD_NO_STRIPE_TOKEN, UPDATE_CARD_EMPTY_FIELDS, \
    BANK_CARD_ALREADY_USED, UPDATE_CARD_NO_ID, UPDATE_CARD_INVALID_ID
from ui_messages.messages.custom_error_titles import CREATE_LISTING_EMPTY_FIELDS_TITLE
from utility.stripe_api import stripe_create_customer, stripe_retrieve_customer, stripe_retrieve_card_info, \
    stripe_retrieve_card, stripe_update_card_info
from utility.user_utility import update_user_last_activity, check_user_suspension_status

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


# add new card and create stripe card/customer
@route('user/cards')
class CardHandler(ApiHandler):
    allowed_methods = ('POST', 'GET', 'PUT')

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

        # first try create stripe customer object
        stripe_response = stripe_create_customer(stripe_token, 'Hawkist_user_%s' % self.user.id)
        logger.debug('CREATE_CUSTOMER_STRIPE_RESPONSE')
        logger.debug(stripe_response)
        stripe_error, stripe_data = stripe_response['error'], stripe_response['data']
        if stripe_error:
            return self.make_error(stripe_error)

        # get customer id and card id from stripe response
        customer_id = stripe_response['id']
        stripe_card_id = stripe_response['sources']['data'][0]['id']

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
            return self.make_error('NO STRIPE CUSTOMER')

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