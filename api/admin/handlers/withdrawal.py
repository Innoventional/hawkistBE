import csv
import logging
import datetime
from api.admin.handlers.login import AdminBaseHandler
from api.bank_accounts.models import UserWithdrawal, WithdrawalStatus
from base import HttpRedirect
from helpers import route

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

        # write into csv
        with open('test.csv', 'w') as fp:
            a = csv.writer(fp, delimiter=',')
            data = [['Me', 'You'],
                    ['293', '219'],
                    ['54', '13']]
            a.writerows(data)

        logger.debug(self.user)
