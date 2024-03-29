import logging
import datetime
from sqlalchemy import and_
from api.admin.handlers.login import AdminBaseHandler
from api.bank_accounts.models import UserWithdrawal, WithdrawalStatus
from base import HttpRedirect
from helpers import route
from utility.amazon import upload_file_withdrawals
from utility.send_email import user_withdrawal_completed_email

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('admin/withdrawals/(.*)')
class AdminWithdrawalsHandler(AdminBaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST')

    def read(self, withdrawal_status):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        withdrawals = self.session.query(UserWithdrawal).order_by(UserWithdrawal.id)

        if withdrawal_status == 'in_progress':
            withdrawals = withdrawals.filter(UserWithdrawal.status == WithdrawalStatus.InProcess).order_by(UserWithdrawal.updated_at)
            template_name = 'admin/withdrawal/admin_withdrawal_in_progress.html'
        elif withdrawal_status == 'completed':
            withdrawals = withdrawals.filter(UserWithdrawal.status == WithdrawalStatus.Completed).order_by(UserWithdrawal.updated_at)
            template_name = 'admin/withdrawal/admin_withdrawal_completed.html'
        else:
            withdrawals = withdrawals.filter(UserWithdrawal.status == WithdrawalStatus.New).order_by(UserWithdrawal.updated_at)
            template_name = 'admin/withdrawal/admin_withdrawal_new.html'

        return self.render_string(template_name, withdrawals=withdrawals,
                                  menu_tab_active='tab_withdrawals', timedelta=datetime.timedelta)

    def create(self, withdrawal_status):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        # get all new withdrawals
        withdrawals = self.session.query(UserWithdrawal).filter(UserWithdrawal.status == WithdrawalStatus.New).order_by(UserWithdrawal.id)
        if withdrawals.count() == 0:
            return self.make_error('No withdrawals to download')
        # write into csv
        filename = 'Hawkist_withdrawals_{0}'.format((datetime.datetime.utcnow() + datetime.timedelta(hours=1)).strftime("%Y-%m-%d_%H:%M"))
        data = 'Withdrawal id, Requested time, Account Holder, Account Number, Sort Code, Email address, ' \
               'Balance to Withdraw, Reference\n'
        for w in withdrawals:
            current_row = '{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}\n'.format(w.id,
                           (w.created_at + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"), w.account_holder,
                           w.account_number, w.account_sort_code, w.user_email, "%.02f" % float(w.amount), w.user_id)
            # marked withdrawals as in process
            w.status = WithdrawalStatus.InProcess
            w.updated_at = datetime.datetime.utcnow()
            data += current_row

        # load this file to amazon
        file_url = upload_file_withdrawals('{0}'.format(filename), data, content_type='scv')
        self.session.commit()
        return self.success({'message': file_url})

    def update(self, withdrawal_status):
        if not self.user:
            return HttpRedirect('/api/admin/login')

        logger.debug(self.user)

        ids = self.get_arg('ids')
        id_list = ids.split(',')
        withdrawals = self.session.query(UserWithdrawal).filter(and_(UserWithdrawal.id.in_(id_list),
                                                                     UserWithdrawal.status == WithdrawalStatus.InProcess))

        for w in withdrawals:
            w.status = WithdrawalStatus.Completed
            w.updated_at = datetime.datetime.utcnow()

            # send notification to user
            user_withdrawal_completed_email(w.user_email, w.user_username, "%.02f" % float(w.amount))
        self.session.commit()
        return self.success()
