import decimal
import logging
import datetime
from api.users.models import User
from base import ApiHandler, die
from api.bank_accounts.models import UserWithdrawal
from environment import env
from helpers import route
from ui_messages.errors.my_balance_errors import BALANCE_EDIT_USER_INFO_EMPTY_FIELDS, \
    BALANCE_EDIT_BANK_ACCOUNT_INFO_EMPTY_FIELDS, BALANCE_EDIT_BANK_ADDRESS_INFO_EMPTY_FIELDS, \
    BALANCE_EDIT_BANK_ACCOUNT_INFO_INVALID_SORT_CODE_FORMAT, BALANCE_EDIT_BANK_ACCOUNT_INFO_INVALID_NUMBER_FORMAT, \
    BALANCE_WITHDRAWAL_NOT_ENOUGH_MONEY
from ui_messages.messages.custom_error_titles import CREATE_LISTING_EMPTY_FIELDS_TITLE, INVALID_NUMBER_FORMAT_TITLE, \
    INVALID_SORT_CODE_FORMAT_TITLE
from utility.send_email import user_withdrawal_requested_email
from utility.stripe_api import stripe_create_transfer
from utility.user_utility import update_user_last_activity, check_user_suspension_status

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('make_me_money/(.*)')
class WalletHandler(ApiHandler):
    allowed_methods = ('GET', )

    def read(self, user_id):
        try:
            user = self.session.query(User).filter(User.id == user_id).first()
            user.app_wallet = 99.99
            self.session.commit()
            return self.success({'message': 'Congrats! You get 99.99!'})
        except:
            return self.make_error('something wrong!\nLiubov')


@route('user/banking/wallet')
class WalletHandler(ApiHandler):
    allowed_methods = ('GET', )

    def read(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        # check does this user has stripe customer
        need_commit = False
        if not self.user.app_wallet:
            self.user.app_wallet = 0
            need_commit = True

        if not self.user.app_wallet_pending:
            self.user.app_wallet_pending = 0
            need_commit = True

        if need_commit:
            self.user.updated_at = datetime.datetime.utcnow()
            self.session.commit()

        return self.success(
            {
                'balance': {
                    'available': "%.02f" % float(self.user.app_wallet),
                    'pending': "%.02f" % float(self.user.app_wallet_pending)
                }
            }
        )


@route('user/banking/user_info')
class BalanceHandler(ApiHandler):
    allowed_methods = ('GET', 'PUT')

    def read(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        return self.success({'user_info': self.user.banking_user_info})

    def update(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        first_name = ''
        last_name = ''
        birth_date = ''
        birth_month = ''
        birth_year = ''

        if self.request_object:
            if 'first_name' in self.request_object:
                first_name = self.request_object['first_name']

            if 'last_name' in self.request_object:
                last_name = self.request_object['last_name']

            if 'birth_date' in self.request_object:
                birth_date = self.request_object['birth_date']

            if 'birth_month' in self.request_object:
                birth_month = self.request_object['birth_month']

            if 'birth_year' in self.request_object:
                birth_year = self.request_object['birth_year']

        empty_field_error = []

        if not first_name:
            empty_field_error.append('first name')

        if not last_name:
            empty_field_error.append('last name')

        if not birth_date or not birth_month or not birth_year:
            empty_field_error.append('birth info')

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
            return self.make_error(message=BALANCE_EDIT_USER_INFO_EMPTY_FIELDS % empty_fields,
                                   title=CREATE_LISTING_EMPTY_FIELDS_TITLE % empty_fields_title.capitalize())

        need_commit = False

        if self.user.first_name != first_name:
            self.user.first_name = first_name
            need_commit = True

        if self.user.last_name != last_name:
            self.user.last_name = last_name
            need_commit = True

        if self.user.birth_date != birth_date:
            self.user.birth_date = birth_date
            need_commit = True

        if self.user.birth_month != birth_month:
            self.user.birth_month = birth_month
            need_commit = True

        if self.user.birth_year != birth_year:
            self.user.birth_year = birth_year
            need_commit = True

        if need_commit:
            self.user.updated_at = datetime.datetime.utcnow()
            self.session.commit()

        return self.success()


@route('user/banking/account')
class BankAccountHandler(ApiHandler):
    allowed_methods = ('GET', 'PUT')

    def read(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        return self.success({'account': self.user.banking_account})

    def update(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        holder_first_name = ''
        holder_last_name = ''
        number = ''
        sort_code = ''

        if self.request_object:
            if 'holder_first_name' in self.request_object:
                holder_first_name = self.request_object['holder_first_name']

            if 'holder_last_name' in self.request_object:
                holder_last_name = self.request_object['holder_last_name']

            if 'number' in self.request_object:
                number = self.request_object['number']

            if 'sort_code' in self.request_object:
                sort_code = self.request_object['sort_code']

        empty_field_error = []

        if not holder_first_name:
            empty_field_error.append('holder first name')

        if not holder_last_name:
            empty_field_error.append('holder last name')

        if not number:
            empty_field_error.append('number')

        if not sort_code:
            empty_field_error.append('sort code')

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
            return self.make_error(message=BALANCE_EDIT_BANK_ACCOUNT_INFO_EMPTY_FIELDS % empty_fields,
                                   title=CREATE_LISTING_EMPTY_FIELDS_TITLE % empty_fields_title.capitalize())

        # length validation
        if len(str(number)) != 8:
            return self.make_error(message=BALANCE_EDIT_BANK_ACCOUNT_INFO_INVALID_NUMBER_FORMAT,
                                   title=INVALID_NUMBER_FORMAT_TITLE)

        if len(str(sort_code)) != 6:
            return self.make_error(message=BALANCE_EDIT_BANK_ACCOUNT_INFO_INVALID_SORT_CODE_FORMAT,
                                   title=INVALID_SORT_CODE_FORMAT_TITLE)
        need_commit = False

        if self.user.bank_account_first_name != holder_first_name:
            self.user.bank_account_first_name = holder_first_name
            need_commit = True

        if self.user.bank_account_last_name != holder_last_name:
            self.user.bank_account_last_name = holder_last_name
            need_commit = True

        if self.user.bank_account_number != number:
            self.user.bank_account_number = number
            need_commit = True

        if self.user.bank_account_sort_code != sort_code:
            self.user.bank_account_sort_code = sort_code
            need_commit = True

        if need_commit:
            self.user.updated_at = datetime.datetime.utcnow()
            self.session.commit()

        return self.success()

@route('user/banking/address')
class BankAddressHandler(ApiHandler):
    allowed_methods = ('GET', 'PUT')

    def read(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        return self.success({'address': self.user.banking_address})

    def update(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)
        update_user_last_activity(self)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        address_line1 = ''
        address_line2 = ''
        city = ''
        post_code = ''

        if self.request_object:
            if 'address_line1' in self.request_object:
                address_line1 = self.request_object['address_line1']

            if 'address_line2' in self.request_object:
                address_line2 = self.request_object['address_line2']

            if 'city' in self.request_object:
                city = self.request_object['city']

            if 'post_code' in self.request_object:
                post_code = self.request_object['post_code']

        empty_field_error = []

        if not address_line1:
            empty_field_error.append('address line 1')

        if not city:
            empty_field_error.append('city')

        if not post_code:
            empty_field_error.append('post code')

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
            return self.make_error(message=BALANCE_EDIT_BANK_ADDRESS_INFO_EMPTY_FIELDS % empty_fields,
                                   title=CREATE_LISTING_EMPTY_FIELDS_TITLE % empty_fields_title.capitalize())

        need_commit = False

        if self.user.bank_account_address_line1 != address_line1:
            self.user.bank_account_address_line1 = address_line1
            need_commit = True

        if address_line2 and self.user.bank_account_address_line2 != address_line2:
            self.user.bank_account_address_line2 = address_line2
            need_commit = True

        if self.user.bank_account_city != city:
            self.user.bank_account_city = city
            need_commit = True

        if self.user.bank_account_post_code != post_code:
            self.user.bank_account_post_code = post_code
            need_commit = True

        if need_commit:
            self.user.updated_at = datetime.datetime.utcnow()
            self.session.commit()

        return self.success()


@route('user/banking/withdrawal')
class WithdrawalHandler(ApiHandler):
    allowed_methods = ('PUT', )

    def update(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)

        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        # check user balance
        if self.user.app_wallet < 15:
            return self.make_error(BALANCE_WITHDRAWAL_NOT_ENOUGH_MONEY)

        # first calculate withdrawal amount
        transfer_amount_total = self.user.app_wallet
        # amount without withdrawal fee
        transfer_amount = decimal.Decimal(transfer_amount_total) - decimal.Decimal(env['stripe_hawkist_fee_withdrawal'])

        # create stripe transfer
        # stripe_response = stripe_create_transfer(amount=transfer_amount_total * 100, user_id=self.user.id)
        # logger.debug('STRIPE_TRANSFER_RESPONSE')
        # logger.debug(stripe_response)
        # stripe_error, stripe_data = stripe_response['error'], stripe_response['data']
        # if stripe_error:
        #     return self.make_error(stripe_error)

        # create withdrawal
        new_withdrawal = UserWithdrawal()
        new_withdrawal.created_at = datetime.datetime.utcnow()
        # new_withdrawal.stripe_transfer_id = stripe_data.id
        new_withdrawal.stripe_transfer_id = 'transfer_test'

        # info about user
        new_withdrawal.user_id = self.user.id
        new_withdrawal.user_username = self.user.username
        new_withdrawal.user_email = self.user.email

        # bank user info
        new_withdrawal.account_holder = '{0} {1}'.format(self.user.bank_account_first_name,
                                                         self.user.bank_account_last_name)
        new_withdrawal.account_number = self.user.bank_account_number
        new_withdrawal.account_sort_code = self.user.bank_account_sort_code

        # transfer info
        new_withdrawal.amount_total = transfer_amount_total
        new_withdrawal.amount = transfer_amount

        self.session.add(new_withdrawal)

        self.user.app_wallet = 0

        self.session.commit()

        user_withdrawal_requested_email(self.user.email, self.user.username, "%.02f" % float(new_withdrawal.amount_total))

        return self.success()