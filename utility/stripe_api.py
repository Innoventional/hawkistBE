import logging
import stripe
from environment import env
from ui_messages.errors.utility_errors.stripe_api_errors import STRIPE_INVALID_TOKEN, STRIPE_TOKEN_ALREADY_USED

__author__ = 'ne_luboff'

# for a test
# stripe.api_key = 'sk_test_O8ks294fD18Z2W9CvaKqiRCa'

stripe.api_key = env['stripe_api_key']

logger = logging.getLogger(__name__)


def stripe_create_customer(token, cardholder):
    customer = ''
    error = ''
    try:
        customer = stripe.Customer.create(
            source=token,
            description='%s stripe account' % cardholder
        )
    except stripe.error.InvalidRequestError, e:
        logger.debug(str(e))
        if 'No such token' in str(e):
            error = STRIPE_INVALID_TOKEN
    finally:
        return {
            'data': customer,
            'error': error
        }


def stripe_add_new_card(customer, token):
    error = ''
    try:
        customer.sources.create(source=token)
    except stripe.error.InvalidRequestError, e:
        logger.debug(str(e))
        if 'No such token' in str(e):
            error = STRIPE_INVALID_TOKEN
        elif 'You cannot use a Stripe token more than once':
            error = STRIPE_TOKEN_ALREADY_USED
    finally:
        return error


def stripe_retrieve_customer(customer_id):
    return stripe.Customer.retrieve(customer_id)


def stripe_retrieve_card(customer, card_id):
    return customer.sources.retrieve(card_id)


# function for getting all card info
def stripe_retrieve_card_info(card):
    return {
        'id': card['id'],
        'last4': card['last4'],
        'city': card['address_city'],
        'postcode': card['address_zip'],
        'address_line1': card['address_line1'],
        'address_line2': card['address_line2'],
        'name': card['name'],
        'exp_month': card['exp_month'],
        'exp_year': card['exp_year'],
    }


def stripe_update_card_info(card, name=None, address_line1=None, address_line2=None, postcode=None,
                            city=None, exp_month=None, exp_year=None):
    need_commit = False

    if card.name != name:
        card.name = name
        need_commit = True

    if card.address_line1 != address_line1:
        card.address_line1 = address_line1
        need_commit = True

    if card.address_line2 != address_line2:
        card.address_line2 = address_line2
        need_commit = True

    if card.address_zip != postcode:
        card.address_zip = postcode
        need_commit = True

    if card.address_city != city:
        card.address_city = city
        need_commit = True

    if card.exp_month != exp_month:
        card.exp_month = exp_month
        need_commit = True

    if card.exp_year != exp_year:
        card.exp_year = exp_year
        need_commit = True

    if need_commit:
        card.save()

# "address_city": null,
#   "address_country": null,
#   "address_line1": null,
#   "address_line1_check": null,
#   "address_line2": null,
#   "address_state": null,
#   "address_zip": null,
#   "address_zip_check": null,
#   "brand": "Visa",
#   "country": "US",
#   "customer": "cus_6hj6xWiBBKO1rH",
#   "cvc_check": "pass",
#   "dynamic_last4": null,
#   "exp_month": 8,
#   "exp_year": 2016,
#   "fingerprint": "HAoWaNuylF5LQwTi",
#   "funding": "credit",
#   "id": "card_16Vi1AArfhEk5XzXC2GRK4tL",
#   "last4": "1881",
#   "metadata": {},
#   "name": null,
#   "object": "card",
#   "tokenization_method": null

def stripe_get_customer(token):
    customer = stripe.Customer.retrieve("cus_6hj6xWiBBKO1rH")
    card = customer.sources.retrieve("card_16UJeRArfhEk5XzXwbkhgiT4")
    return card


def stripe_update_card(token):
    # first get card
    card = stripe_get_customer('qwq')
    card.name = 'Liubov M)'
    card.save()
    return card


# test stripe customer
if __name__ == '__main__':
    print stripe_update_card('qwqw')

    # first generate token
    # test_card_number = 4242424242424242
    # test_card_exp_month = 12
    # test_card_exp_year = 2019
    # test_card_cvc = 123
    # card_object = stripe.Token.create(
    #     card={
    #         "number": test_card_number,
    #         "exp_month": test_card_exp_month,
    #         "exp_year": test_card_exp_year,
    #         "cvc": test_card_cvc
    #     },
    #     )
    # print card_object
    """
    {
        "card":
            {
                "address_city": null,
                "address_country": null,
                "address_line1": null,
                "address_line1_check": null,
                "address_line2": null,
                "address_state": null,
                "address_zip": null,
                "address_zip_check": null,
                "brand": "Visa",
                "country": "US",
                "cvc_check": "unchecked",
                "dynamic_last4": null,
                "exp_month": 12,
                "exp_year": 2019,
                "fingerprint": "nIzQ9tYgjDWZLGSB",
                "funding": "credit",
                "id": "card_16UJeRArfhEk5XzXwbkhgiT4",
                "last4": "4242",
                "metadata": {},
                "name": null,
                "object": "card",
                "tokenization_method": null
            },
        "client_ip": "217.12.211.214",
        "created": 1438272779,
        "id": "tok_16UJeRArfhEk5XzXHdfBs3ny",
        "livemode": false,
        "object": "token",
        "type": "card",
        "used": false
    }
    """
    # card_token = card_object.get('id')
    # customer = stripe_create_customer(card_token, 'Liubov test')

    # customer = stripe_create_customer('asasasas', 'Liubov test')
    # print customer
    """
    {
        "account_balance": 0,
        "created": 1438272780,
        "currency": null,
        "default_source": "card_16UJeRArfhEk5XzXwbkhgiT4",
        "delinquent": false,
        "description": "Liubov test stripe account",
        "discount": null,
        "email": null,
        "id": "cus_6hj6xWiBBKO1rH",
        "livemode": false,
        "metadata": {},
        "object": "customer",
        "sources": {
            "data": [
                {
                    "address_city": null,
                    "address_country": null,
                    "address_line1": null,
                    "address_line1_check": null,
                    "address_line2": null,
                    "address_state": null,
                    "address_zip": null,
                    "address_zip_check": null,
                    "brand": "Visa",
                    "country": "US",
                    "customer": "cus_6hj6xWiBBKO1rH",
                    "cvc_check": "pass",
                    "dynamic_last4": null,
                    "exp_month": 12,
                    "exp_year": 2019,
                    "fingerprint": "nIzQ9tYgjDWZLGSB",
                    "funding": "credit",
                    "id": "card_16UJeRArfhEk5XzXwbkhgiT4",
                    "last4": "4242",
                    "metadata": {},
                    "name": null,
                    "object": "card",
                    "tokenization_method": null
                }
            ],
            "has_more": false,
            "object": "list",
            "total_count": 1,
            "url": "/v1/customers/cus_6hj6xWiBBKO1rH/sources"
        },
        "subscriptions": {
            "data": [],
            "has_more": false,
            "object": "list",
            "total_count": 0,
            "url": "/v1/customers/cus_6hj6xWiBBKO1rH/subscriptions"
            }
    }
    """
