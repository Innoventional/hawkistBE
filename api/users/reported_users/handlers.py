import logging
import datetime
from api.users.models import User
from api.users.reported_users.models import ReportedUsers
from api.users.reported_users.models import UserReportingReasons
from base import ApiHandler, die
from helpers import route
from ui_messages.errors.followers_errors.followers_errors import INVALID_USER_ID
from ui_messages.errors.users_errors.reported_users_errors import REPORT_USER_NO_USER_ID, \
    REPORT_USER_TRY_REPORT_YOURSELF, REPORT_USER_ALREADY_BLOCKED_USER, REPORT_USER_NO_REASON_ID, \
    REPORT_USER_INVALID_REASON_ID
from ui_messages.errors.users_errors.update_errors import NO_USER_WITH_ID
from utility.user_utility import update_user_last_activity, check_user_suspension_status

__author__ = 'ne_luboff'

logger = logging.getLogger(__name__)


@route('user/reporting')
class ReportUsersHandler(ApiHandler):
    allowed_methods = ('POST', )

    def create(self):
        if self.user is None:
            die(401)

        logger.debug(self.user)

        # check user status
        suspension_error = check_user_suspension_status(self.user)
        if suspension_error:
            logger.debug(suspension_error)
            return suspension_error

        update_user_last_activity(self)

        logger.debug('REQUEST_OBJECT_REPORT_USER')
        logger.debug(self.request_object)

        user_to_report_id = None
        user_report_reason = None

        # try get id and reason to report user
        if self.request_object:
            if 'user_id' in self.request_object:
                user_to_report_id = self.request_object['user_id']

            if 'reason_id' in self.request_object:
                user_report_reason = self.request_object['reason_id']

        if not user_to_report_id:
            return self.make_error(REPORT_USER_NO_USER_ID)

        if len(str(user_report_reason)):
            return self.make_error(REPORT_USER_NO_REASON_ID)

        # validate user id
        try:
            user_to_report_id = int(user_to_report_id)
        except:
            return self.make_error(INVALID_USER_ID % user_to_report_id.upper())

        # maybe you try report yourself
        if str(self.user.id) == str(user_to_report_id):
            return self.make_error(REPORT_USER_TRY_REPORT_YOURSELF)

        # try get user to report by id
        user_to_report = self.session.query(User).get(user_to_report_id)

        # if where is no user to report in our db
        if not user_to_report:
            return self.make_error(NO_USER_WITH_ID % user_to_report_id)

        # check do you block this user
        if user_to_report in self.user.blocked:
            return self.make_error(REPORT_USER_ALREADY_BLOCKED_USER % user_to_report.username.upper())

        # check reporting reason
        if not UserReportingReasons.tostring(user_report_reason):
            return self.make_error(REPORT_USER_INVALID_REASON_ID % user_report_reason)

        # else add new report about this user
        report = ReportedUsers()
        report.created_at = datetime.datetime.utcnow()
        report.updated_at = datetime.datetime.utcnow()
        report.user_id = self.user.id
        report.reported_user_id = user_to_report.id
        report.reason = user_report_reason

        self.session.add(report)
        self.session.commit()

        return self.success()