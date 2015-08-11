# import logging
import stripe
# from environment import env
# from ui_messages.errors.utility_errors.stripe_api_errors import STRIPE_INVALID_TOKEN, STRIPE_TOKEN_ALREADY_USED, \
#     STRIPE_BAD_CONNECTION
from ui_messages.errors.utility_errors.stripe_api_errors import STRIPE_INVALID_CARD_EXP_YEAR
from ui_messages.messages.custom_error_titles import STRIPE_INVALID_CARD_EXP_YEAR_TITLE

__author__ = 'ne_luboff'

# for a test
stripe.api_key = 'sk_test_O8ks294fD18Z2W9CvaKqiRCa'

# stripe.api_key = env['stripe_api_key']
#
# logger = logging.getLogger(__name__)

"""
Stripe api handler.
More info about stripe api:
    https://stripe.com/docs/api#intro
"""


def stripe_create_customer(token, cardholder):
    """
    Create new stripe customer.
    Send token to stripe api and get customer object and card object in request.
    User cardholder for easy customer identification.
    Parameters:
        token - stripe token, string;
        cardholder - string.
    Customer object:
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
    customer = ''
    error = ''
    try:
        customer = stripe.Customer.create(
            source=token,
            description='Hawkist_user_%s stripe account' % cardholder
        )
    except stripe.error.InvalidRequestError, e:
        error = str(e)
        # logger.debug(str(e))
        # if 'No such token' in str(e):
        #     error = STRIPE_INVALID_TOKEN
    finally:
        return {
            'data': customer,
            'error': error
        }


def stripe_add_new_card(customer, token):
    """
    In case if current Hawkist user already has stripe customer account we should not create new customer.
    We just add new card to existing stripe customer object.
    Parameters:
        customer - stripe customer to add new card, object;
        token - stripe token with card info, string.
    Card object response:
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
    error = ''
    try:
        customer.sources.create(source=token)
    except stripe.error.InvalidRequestError, e:
        error = str(e)
        # logger.debug(str(e))
        # if 'No such token' in str(e):
        #     error = STRIPE_INVALID_TOKEN
        # elif 'You cannot use a Stripe token more than once':
        #     error = STRIPE_TOKEN_ALREADY_USED
    finally:
        return error


def stripe_retrieve_customer(customer_id):
    """
    Function for getting info about stripe customer account by id (parameter customer_id, string).
    Parameter:
        customer_id - stripe customer id, string.
    Returns customer object like in stripe_create_customer function.
    """
    return stripe.Customer.retrieve(customer_id)


def stripe_retrieve_card(customer, card_id):
    """
    Function for getting info about one of cards of current stripe customer by card id.
    Parameters:
        customer - stripe customer, object;
        card_id - card to retrieve id, string.
    Returns response like in stripe_add_new_card
    """
    return customer.sources.retrieve(card_id)


def stripe_retrieve_card_info(card):
    """
    Function for retrieve card info.
    Parameter:
        card - stripe card, object.
    Return next info:
        id - stripe card id, string;
        last4 - last 4 digits of card number;
        city - card address city;
        postcode - card address postcode;
        address_line1 - card address line 1;
        address_line2 - card address line 2;
        name - card holder name;
        exp_month - card expiration month;
        exp_year - card expiration year.
    """
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
    """
    Function for card info updating.
    """
    error = None
    try:
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
    except stripe.error.CardError, e:
        if "Your card's expiration year is invalid." in str(e):
            error = {
                'message': STRIPE_INVALID_CARD_EXP_YEAR,
                'title': STRIPE_INVALID_CARD_EXP_YEAR_TITLE
            }
        else:
            error = str(e)
    finally:
        return error


def stripe_delete_card(card):
    """
    Function for stripe card deletion
    """
    error = ''
    try:
        card.delete()
    except stripe.error.APIConnectionError, e:
        error = str(e)
        # if 'Unexpected error communicating with Stripe' in str(e):
        #     error = STRIPE_BAD_CONNECTION
    finally:
        return error


def stripe_check_balance():
    pass


def stripe_create_charges(customer_id=None, card_id=None, amount=None, currency='gbp', description=None):
    """
    Function for charges.
    Parameters:
        customer_id - stripe customer id, string;
        card_id - stripe card which will be debited id,
        amount - amount of money which will be debited in cents, integer;
        currency - payment currency, gbp by default;
        description - payment description for easy payment identification.
    Charges response:
        {
            "amount": 1200,
            "amount_refunded": 0,
            "application_fee": null,
            "balance_transaction": "txn_16W2GNArfhEk5XzXgE6apPib",
            "captured": true,
            "created": 1438682595,
            "currency": "gbp",
            "customer": "cus_6hj6xWiBBKO1rH",
            "description": "ne_luboff test charge",
            "destination": null,
            "dispute": null,
            "failure_code": null,
            "failure_message": null,
            "fraud_details": {},
            "id": "ch_16W2GNArfhEk5XzXIGuzaF3z",
            "invoice": null,
            "livemode": false,
            "metadata": {},
            "object": "charge",
            "paid": true,
            "receipt_email": null,
            "receipt_number": null,
            "refunded": false,
            "refunds": {
                "data": [],
                "has_more": false,
                "object": "list",
                "total_count": 0,
                "url": "/v1/charges/ch_16W2GNArfhEk5XzXIGuzaF3z/refunds"
            },
            "shipping": null,
            "source": {
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
                "cvc_check": null,
                "dynamic_last4": null,
                "exp_month": 12,
                "exp_year": 2019,
                "fingerprint": "nIzQ9tYgjDWZLGSB",
                "funding": "credit",
                "id": "card_16UJeRArfhEk5XzXwbkhgiT4",
                "last4": "4242",
                "metadata": {},
                "name": "Liubov M)",
                "object": "card",
                "tokenization_method": null
            },
            "statement_descriptor": null,
            "status": "succeeded"
        }
    """
    error = ''
    charge = ''
    try:
        charge = stripe.Charge.create(
            amount=amount,
            currency=currency,
            customer=customer_id,
            source=card_id,
            description='Hawkist_listing_%s' % description
        )
    except stripe.error.CardError, e:
        error = str(e)
    except stripe.error.InvalidRequestError, e:
        error = str(e)
    except stripe.error.AuthenticationError, e:
        error = str(e)
    except stripe.error.APIConnectionError, e:
        error = str(e)
    except stripe.error.StripeError, e:
        error = str(e)
    except Exception, e:
        error = str(e)
    finally:
        return {
            'error': error,
            'data': charge
        }


def stripe_refund(charge_id):
    """
    Refund money function.
    Return all charged money to customer.
    """
    error = ''
    refund = ''
    try:
        # first get charge by id
        charge = stripe.Charge.retrieve(charge_id)
        # then refund it
        refund = charge.refunds.create()
    except stripe.error.CardError, e:
        error = str(e)
    except stripe.error.InvalidRequestError, e:
        error = str(e)
    except stripe.error.AuthenticationError, e:
        error = str(e)
    except stripe.error.APIConnectionError, e:
        error = str(e)
    except stripe.error.StripeError, e:
        error = str(e)
    except Exception, e:
        error = str(e)
    finally:
        return {
            'error': error,
            'data': refund
        }


def stripe_create_transfer(destination=None, amount=None, currency='gbp', description=None,
                           charge=None, customer_id=None, card_id=None):
    error = ''
    transfer = ''
    try:
        # charge = stripe.Charge.create(
        #     amount=amount,
        #     currency=currency,
        #     destination=destination_card_id,
        #     customer=customer_id,
        #     source=card_id,
        #     description='Hawkist_payment_for_listing_%s' % description
        # )
        transfer = stripe.Transfer.create(
            amount=amount,
            destination=destination,
            description=description,
            currency=currency,
            source_transaction=charge
        )
        # charge = stripe.Transfer.create(
        #     amount=amount,
        #     currency=currency,
        #     destination=destination_card_id,
        #     source_transaction=destination_card_id,
        #     description='Hawkist_payment_for_listing_%s' % description
        # )
    except stripe.error.CardError, e:
        error = str(e)
    except stripe.error.InvalidRequestError, e:
        error = str(e)
    except stripe.error.AuthenticationError, e:
        error = str(e)
    except stripe.error.APIConnectionError, e:
        error = str(e)
    except stripe.error.StripeError, e:
        error = str(e)
    except Exception, e:
        error = str(e)
    finally:
        return {
            'error': error,
            'data': transfer
        }


def stripe_test(amount=None, customer=None, destination=None, card=None):
    error = ''
    charge = ''
    try:
        # first create token for payment
        charge = stripe.Charge.create(
            amount=amount,
            currency='gbp',
            customer=customer,
            card=card,
            destination=destination
        )
        # charge = stripe.Transfer.create(
        #     amount=amount,
        #     currency=currency,
        #     destination=destination_card_id,
        #     source_transaction=destination_card_id,
        #     description='Hawkist_payment_for_listing_%s' % description
        # )
    except stripe.error.CardError, e:
        error = str(e)
    except stripe.error.InvalidRequestError, e:
        error = str(e)
    except stripe.error.AuthenticationError, e:
        error = str(e)
    except stripe.error.APIConnectionError, e:
        error = str(e)
    except stripe.error.StripeError, e:
        error = str(e)
    except Exception, e:
        error = str(e)
    finally:
        return {
            'error': error,
            'data': charge
        }


def stripe_create_recipient():
    r = stripe.Recipient.create(
        name="John Doe",
        type="individual"
    )
    return r


# test stripe customer
if __name__ == '__main__':
    print 'In utility/stripe_api'
    # print stripe_refund('ch_16W6vIArfhEk5XzXKfbubPkP')
    print stripe_create_recipient()
    # print stripe_create_charges(customer_id='cus_6hj6xWiBBKO1rH', card_id='card_16UJeRArfhEk5XzXwbkhgiT4', amount=1200,
    #                             description='ne_luboff test charge')
    # print stripe_create_transfer(destination_card_id='cus_6jDv0u0vdbtIPH', source_transaction='cus_6jDv0u0vdbtIPH', amount=1000,
    #                              description='test', customer_id='cus_6hj6xWiBBKO1rH', card_id='card_16UJeRArfhEk5XzXwbkhgiT4')

    # print stripe_create_transfer(destination='cus_6jDv0u0vdbtIPH', amount=1000, description='test',
    #                              charge='ch_16W6vIArfhEk5XzXKfbubPkP')
    # print stripe_test(amount=1234, customer='cus_6hj6xWiBBKO1rH', destination='cus_6jDv0u0vdbtIPH',
    #                   card='card_16UJeRArfhEk5XzXwbkhgiT4')
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
