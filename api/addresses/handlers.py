import logging
import datetime
from api.addresses.models import Address
from base import ApiHandler, die
from helpers import route
from ui_messages.errors.addresses_error import ADD_ADDRESS_MISSING_FIELDS, UPDATE_ADDRESS_MISSING_FIELDS, \
    ADDRESS_INVALID_ID, DELETE_ADDRESS_NO_ID, ADD_ADDRESS_GET_LATEST_NO_CARD
from ui_messages.messages.custom_error_titles import CREATE_LISTING_EMPTY_FIELDS_TITLE, \
    ADD_ADDRESS_GET_LATEST_NO_CARD_TITLE
from utility.stripe_api import stripe_retrieve_customer
from utility.user_utility import update_user_last_activity, check_user_suspension_status

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('user/addresses')
class AddressHandler(ApiHandler):
    allowed_methods = ('GET', 'POST', 'DELETE', 'PUT')

    def read(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        return self.success({
            'addresses': [a.response for a in self.session.query(Address).filter(Address.user_id == self.user.id)]
        })

    def create(self):

        if self.user is None:
            die(401)

        logger.debug(self.user)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)
        logger.debug(self.request_object)

        address_id = ''
        address_line1 = ''
        address_line2 = ''
        postcode = ''
        city = ''

        if self.request_object:
            if 'id' in self.request_object:
                address_id = self.request_object['id']

            if 'address_line1' in self.request_object:
                address_line1 = self.request_object['address_line1']

            if 'address_line2' in self.request_object:
                address_line2 = self.request_object['address_line2']

            if 'postcode' in self.request_object:
                postcode = self.request_object['postcode']

            if 'city' in self.request_object:
                city = self.request_object['city']

        empty_field_error = []

        if not address_line1:
            empty_field_error.append('address line')

        if not city:
            empty_field_error.append('city')

        if not postcode:
            empty_field_error.append('postcode')

        # check is it create or update request
        if address_id:
            # try get address
            address = self.session.query(Address).get(address_id)
            if not address:
                return self.make_error(ADDRESS_INVALID_ID % address_id)

            if empty_field_error:
                if len(empty_field_error) == 2:
                    empty_fields = ' and '.join(empty_field_error)
                    empty_fields_title = ' & '.join(empty_field_error)
                else:
                    empty_fields = ', '.join(empty_field_error)
                    last_coma_index = empty_fields.rfind(',')
                    empty_fields = empty_fields[:last_coma_index] + \
                                   empty_fields[last_coma_index:].replace(', ', ' and ')
                    empty_fields_title = empty_fields[:last_coma_index] + \
                                         empty_fields[last_coma_index:].replace(' and ', ' & ')
                return self.make_error(message=UPDATE_ADDRESS_MISSING_FIELDS % empty_fields,
                                       title=CREATE_LISTING_EMPTY_FIELDS_TITLE % empty_fields_title.capitalize())

            need_commit = False

            if address.address_line1 != address_line1:
                address.address_line1 = address_line1
                need_commit = True

            if address.city != city:
                address.city = city
                need_commit = True

            if address.postcode != postcode:
                address.postcode = postcode
                need_commit = True

            if address_line2:
                if address.address_line2 != address_line2:
                    address.address_line2 = address_line2
                    need_commit = True

            if need_commit:
                address.updated_at = datetime.datetime.utcnow()
                self.session.commit()
        else:
            if empty_field_error:
                if len(empty_field_error) == 2:
                    empty_fields = ' and '.join(empty_field_error)
                    empty_fields_title = ' & '.join(empty_field_error)
                else:
                    empty_fields = ', '.join(empty_field_error)
                    last_coma_index = empty_fields.rfind(',')
                    empty_fields = empty_fields[:last_coma_index] + \
                                   empty_fields[last_coma_index:].replace(', ', ' and ')
                    empty_fields_title = empty_fields[:last_coma_index] + \
                                         empty_fields[last_coma_index:].replace(' and ', ' & ')
                return self.make_error(message=ADD_ADDRESS_MISSING_FIELDS % empty_fields,
                                       title=CREATE_LISTING_EMPTY_FIELDS_TITLE % empty_fields_title.capitalize())
            # create new address instance
            new_address = Address()
            new_address.user_id = self.user.id
            new_address.created_at = datetime.datetime.utcnow()
            new_address.updated_at = datetime.datetime.utcnow()

            new_address.address_line1 = address_line1
            new_address.postcode = postcode
            new_address.city = city
            if address_line2:
                new_address.address_line2 = address_line2

            self.session.add(new_address)
            self.session.commit()

        return self.success()

    def remove(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        address_to_delete_id = self.get_arg('address_id', None)

        if not address_to_delete_id:
            return self.make_error(DELETE_ADDRESS_NO_ID)

        address_to_delete = self.session.query(Address).get(address_to_delete_id)
        if not address_to_delete:
            return self.make_error(ADDRESS_INVALID_ID % address_to_delete_id)

        self.session.delete(address_to_delete)
        self.session.commit()
        return self.success()

    # request for getting address info from latest added card
    def update(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        if not self.user.stripe_customer:
            return self.make_error(title=ADD_ADDRESS_GET_LATEST_NO_CARD_TITLE,
                                   message=ADD_ADDRESS_GET_LATEST_NO_CARD)

        stripe_customer = stripe_retrieve_customer(self.user.stripe_customer.stripe_customer_id)

        # check is any card in this stripe account
        stripe_customer_cards = stripe_customer['sources']['data']
        if not stripe_customer_cards:
            return self.make_error(title=ADD_ADDRESS_GET_LATEST_NO_CARD_TITLE,
                                   message=ADD_ADDRESS_GET_LATEST_NO_CARD)
        return self.success({
            'addresses': {
                'address_line1': stripe_customer_cards[-1].address_line1,
                'address_line2': stripe_customer_cards[-1].address_line2,
                'city': stripe_customer_cards[-1].address_city,
                'postcode': stripe_customer_cards[-1].address_zip
            }})